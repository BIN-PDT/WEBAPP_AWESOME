from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    id = models.CharField(
        max_length=100, primary_key=True, editable=False, default=uuid4
    )
    url = models.URLField(max_length=500, null=True)
    artist = models.CharField(max_length=500, null=True)
    title = models.CharField(max_length=500)
    image = models.URLField(max_length=500)
    body = models.TextField()
    author = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="posts"
    )
    tags = models.ManyToManyField("Tag")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ["-created"]


class Tag(models.Model):
    image = models.FileField(upload_to="icons/", null=True, blank=True)
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20, unique=True)
    order = models.IntegerField(null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["order"]


class Comment(models.Model):
    id = models.CharField(
        max_length=100, primary_key=True, editable=False, default=uuid4
    )
    author = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="comments"
    )
    parent_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return f"{self.author.username} : {self.body[:30]}"
        except:
            return f"No author : {self.body[:30]}"

    class Meta:
        ordering = ["-created"]


class Reply(models.Model):
    id = models.CharField(
        max_length=100, primary_key=True, editable=False, default=uuid4
    )
    author = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="replies"
    )
    parent_comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="replies"
    )
    body = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return f"{self.author.username} : {self.body[:30]}"
        except:
            return f"No author : {self.body[:30]}"

    class Meta:
        ordering = ["-created"]
