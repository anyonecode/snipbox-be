from django.urls import path
from .views import (
    SnippetDetailUpdateDeleteView,
    SnippetOverviewCreateView,
)

urlpatterns = [
    path('snippets/', SnippetOverviewCreateView.as_view(), name='snippet-list'),
    path('snippets/<int:pk>/', SnippetDetailUpdateDeleteView.as_view(), name='snippet-detail'),
]