from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Snippet, Tag
from .serializers import (
    SnippetListSerializer,
    SnippetDetailSerializer,
    SnippetWriteSerializer,
    TagSerializer,
)


class SnippetOverviewCreateView(APIView):
    """
    GET  /api/v1/snippets/  — Overview: total count + list with hyperlinks.
    POST /api/v1/snippets/  — Create a new snippet for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            snippets = Snippet.objects.filter(user=request.user)
            serializer = SnippetListSerializer(
                snippets,
                many=True,
                context={'request': request},
            )
            return Response({
                'total': snippets.count(),
                'snippets': serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while fetching snippets.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        if not request.data:
            return Response(
                {'detail': 'Request body cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer = SnippetWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Validate tags list format if provided
            tags = request.data.get('tags', [])
            if not isinstance(tags, list):
                return Response(
                    {'detail': 'Tags must be a list of objects with a "title" field.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            for tag in tags:
                if not isinstance(tag, dict) or 'title' not in tag:
                    return Response(
                        {'detail': 'Each tag must be an object with a "title" field.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not str(tag['title']).strip():
                    return Response(
                        {'detail': 'Tag title cannot be blank.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer.save(user=request.user)
            detail_serializer = SnippetDetailSerializer(
                serializer.instance,
                context={'request': request},
            )
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as exc:
            return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while creating the snippet.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class SnippetDetailUpdateDeleteView(APIView):
    """
    GET    /api/snippets/<pk>/  — Retrieve a snippet (owner only).
    PUT    /api/snippets/<pk>/  — Full update of a snippet.
    PATCH  /api/snippets/<pk>/  — Partial update of a snippet.
    DELETE /api/snippets/<pk>/  — Delete snippet; returns remaining list.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Return the snippet owned by this user or None."""
        try:
            return Snippet.objects.get(pk=pk, user=user)
        except Snippet.DoesNotExist:
            return None

    def _not_found_response(self):
        return Response(
            {'detail': 'Snippet not found or you do not have permission to access it.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    def get(self, request, pk):
        try:
            snippet = self.get_object(pk, request.user)
            if snippet is None:
                return self._not_found_response()
            serializer = SnippetDetailSerializer(snippet, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while fetching the snippet.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update(self, request, pk, partial=False):
        """Shared logic for PUT and PATCH."""
        if not request.data:
            return Response(
                {'detail': 'Request body cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            snippet = self.get_object(pk, request.user)
            if snippet is None:
                return self._not_found_response()

            serializer = SnippetWriteSerializer(snippet, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            # Validate tags format when provided
            tags = request.data.get('tags')
            if tags is not None:
                if not isinstance(tags, list):
                    return Response(
                        {'detail': 'Tags must be a list of objects with a "title" field.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                for tag in tags:
                    if not isinstance(tag, dict) or 'title' not in tag:
                        return Response(
                            {'detail': 'Each tag must be an object with a "title" field.'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if not str(tag['title']).strip():
                        return Response(
                            {'detail': 'Tag title cannot be blank.'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            serializer.save()
            detail_serializer = SnippetDetailSerializer(
                serializer.instance,
                context={'request': request},
            )
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        except ValidationError as exc:
            return Response({'detail': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while updating the snippet.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def delete(self, request, pk):
        try:
            snippet = self.get_object(pk, request.user)
            if snippet is None:
                return self._not_found_response()
            snippet.delete()
            remaining = Snippet.objects.filter(user=request.user)
            serializer = SnippetListSerializer(
                remaining,
                many=True,
                context={'request': request},
            )
            return Response({
                'total': remaining.count(),
                'snippets': serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while deleting the snippet.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TagListView(APIView):
    """
    GET /api/tags/  — List all available tags.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while fetching tags.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TagDetailView(APIView):
    """
    GET /api/tags/<pk>/  — Tag info + all snippets linked to it (current user only).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            tag = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response(
                {'detail': f'Tag with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while fetching the tag.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            tag_serializer = TagSerializer(tag)
            snippets = tag.snippets.filter(user=request.user)
            snippet_serializer = SnippetListSerializer(
                snippets,
                many=True,
                context={'request': request},
            )
            return Response({
                'tag': tag_serializer.data,
                'total_snippets': snippets.count(),
                'snippets': snippet_serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {'detail': 'An error occurred while fetching snippets for tag.', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
