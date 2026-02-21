from django.urls import path
from .views import (
    SnippetDetailUpdateDeleteView,
    SnippetOverviewCreateView,
    TagDetailView,
    TagListView,
)

urlpatterns = [
    path('snippets/', SnippetOverviewCreateView.as_view(), name='snippet-list'),
    path('snippets/<int:pk>/', SnippetDetailUpdateDeleteView.as_view(), name='snippet-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
]