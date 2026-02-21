from rest_framework import serializers
from .models import Snippet, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model."""

    class Meta:
        model = Tag
        fields = ['id', 'title']


class SnippetListSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='snippet-detail',
        lookup_field='pk',
    )

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'url']


class SnippetDetailSerializer(serializers.ModelSerializer):
    """Full read serializer for a single snippet."""

    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'note', 'created_at', 'updated_at', 'tags']


class SnippetWriteSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'note', 'tags']

    def _handle_tags(self, tags_data):
        """Return a list of Tag instances, creating only new ones."""
        tag_instances = []
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(title=tag_data['title'].strip())
            tag_instances.append(tag)
        return tag_instances

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        snippet = Snippet.objects.create(**validated_data)
        snippet.tags.set(self._handle_tags(tags_data))
        return snippet

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(self._handle_tags(tags_data))
        return instance
