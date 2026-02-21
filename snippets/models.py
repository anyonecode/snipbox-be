from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Tag(models.Model):
    """Simple tag model with a unique title."""

    title = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Snippet(models.Model):
    """Short text snippet with title, note, timestamps, owner, and tags."""

    title = models.CharField(max_length=255)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='snippets',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='snippets',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
