from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *


def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            raise Http404()

    return render(request, "a_users/profile.html", {"profile": profile})


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    form = ProfileEditForm(instance=profile)

    if request.method == "POST":
        form = ProfileEditForm(instance=profile, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect("profile")

    return render(request, "a_users/profile_edit.html", {"form": form})


@login_required
def profile_delete_view(request):
    user = request.user

    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "Account deleted, what a pity!")
        return redirect("home")

    return render(request, "a_users/profile_delete.html")
