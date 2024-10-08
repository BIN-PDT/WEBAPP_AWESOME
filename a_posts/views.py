import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import *
from .forms import *


def home_view(request, tag=None):
    posts = Post.objects.all() if not tag else Post.objects.filter(tags__slug=tag)
    paginator = Paginator(posts, 3)
    page = int(request.GET.get("page", 1))

    if page <= paginator.num_pages:
        posts = paginator.page(page)
    else:
        return HttpResponse("")

    context = {"posts": posts, "tag": tag, "page": page}

    if request.htmx:
        return render(request, "snippets/infinite_posts.html", context)
    return render(request, "a_posts/home.html", context)


def post_page_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    comment_form = CommentCreateForm()
    reply_form = ReplyCreateForm()

    if request.htmx:
        if "new" in request.GET:
            comments = post.comments.all()
        else:
            comments = (
                post.comments.annotate(likes_count=Count("likes"))
                .filter(likes_count__gt=0)
                .order_by("-likes_count")
            )

        context = {"comments": comments, "reply_form": reply_form}
        return render(request, "snippets/filter_comments.html", context)

    context = {"post": post, "comment_form": comment_form, "reply_form": reply_form}
    return render(request, "a_posts/post_page.html", context)


@login_required
def post_create_view(request):
    form = PostCreateForm()

    if request.method == "POST":
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            website = requests.get(form.data["url"])
            source = BeautifulSoup(website.text, "html.parser")
            try:
                # GET IMAGE URL.
                image_result = source.select(
                    'meta[content^="https://live.staticflickr.com/"]'
                )
                image = image_result[0]["content"]
                post.image = image
                # GET IMAGE TITLE.
                title_result = source.select("h1.photo-title")
                title = title_result[0].text.strip()
                post.title = title
                # GET IMAGE ARTIST.
                artist_result = source.select("a.owner-name")
                artist = artist_result[0].text.strip()
                post.artist = artist
            except:
                messages.error(request, "The url is not a flickr image url!")
            else:
                # LINK TO USER.
                post.author = request.user

                post.save()
                form.save_m2m()
                return redirect("home")

    return render(request, "a_posts/post_create.html", {"form": form})


@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted")
        return redirect("home")

    return render(request, "a_posts/post_delete.html", {"post": post})


@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    form = PostEditForm(instance=post)

    if request.method == "POST":
        form = PostEditForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated")
            return redirect("home")

    context = {"post": post, "form": form}
    return render(request, "a_posts/post_edit.html", context)


@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)
    reply_form = ReplyCreateForm()

    if request.method == "POST":
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            comment.save()

    context = {"post": post, "comment": comment, "reply_form": reply_form}
    return render(request, "snippets/add_comment.html", context)


@login_required
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, id=pk, author=request.user)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted")
        return redirect("post", comment.parent_post.id)

    return render(request, "a_posts/comment_delete.html", {"comment": comment})


@login_required
def reply_sent(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    reply_form = ReplyCreateForm()

    if request.method == "POST":
        form = ReplyCreateForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_comment = comment
            reply.save()

    context = {"comment": comment, "reply": reply, "reply_form": reply_form}
    return render(request, "snippets/add_reply.html", context)


@login_required
def reply_delete_view(request, pk):
    reply = get_object_or_404(Reply, id=pk, author=request.user)

    if request.method == "POST":
        reply.delete()
        messages.success(request, "Reply deleted")
        return redirect("post", reply.parent_comment.parent_post.id)

    return render(request, "a_posts/reply_delete.html", {"reply": reply})


def like_toggle(model):
    def inner(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            instance = get_object_or_404(model, id=kwargs.get("pk"))

            if instance.author != user:
                if instance.likes.contains(user):
                    instance.likes.remove(user)
                else:
                    instance.likes.add(user)
            return function(request, instance)

        return wrapper

    return inner


@login_required
@like_toggle(Post)
def post_like(request, instance):
    return render(request, "snippets/likes_post.html", {"post": instance})


@login_required
@like_toggle(Comment)
def comment_like(request, instance):
    return render(request, "snippets/likes_comment.html", {"comment": instance})


@login_required
@like_toggle(Reply)
def reply_like(request, instance):
    return render(request, "snippets/likes_reply.html", {"reply": instance})
