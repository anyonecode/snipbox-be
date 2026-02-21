from django.urls import path
from .views import (
    SnippetOverviewCreateView,
)

urlpatterns = [
    path('snippets/', SnippetOverviewCreateView.as_view(), name='snippet-list'),
]