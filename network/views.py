from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count

import json

from .models import User, Followers, Comments, Post


def index(request):
    return render(request, "network/index.html")

def newpost(request):
    if request.method == "POST":
        p = request.POST["post"]
        mynewpost= Post(creator=request.user, post_text=p)
        mynewpost.save()
    return HttpResponseRedirect(reverse("index"))

def getpostsall(request):
    posts = Post.objects.all()
    posts = posts.order_by("-date")
    return JsonResponse([post.serialize() for post in posts], safe=False)

def profile(request, creator):
    print(creator)
    user = User.objects.get(username=creator)
    posts = Post.objects.filter(creator=user)
    #max = bids.objects.filter(listing__id=listing_id).aggregate(Max('bid'))

    followers = Followers.objects.filter(followee=user).count()
    following = Followers.objects.filter(follower=user).count()
    return render(request, "network/profile.html", {
                "profile": user,
                "posts": posts,
                "followers": followers,
                "following": following
    })

def follow(request, user):
    print("user: " + user)
    tofollow = User.objects.get(username=user)
    myfollower = request.user.username
    print("this is " + myfollower)
    if Followers.objects.filter(follower=request.user, followee=tofollow).exists():
        print("already exists")
    elif user == myfollower:
        print("they're the same")
    else:
        newfollow = Followers(follower=request.user, followee=tofollow)
        newfollow.save()
    return HttpResponseRedirect(reverse("profile", args=(user,)))
    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
