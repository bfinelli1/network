from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

import json

from .models import User, Followers, Comments, Post, Likes


def index(request):
    posts = Post.objects.all()
    posts = posts.order_by("-date")
    name = request.user.username

    #paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts,
        "name": name,
        "page_obj": page_obj
    })


def newpost(request):
    if request.method == "POST":
        p = request.POST["post"]
        mynewpost = Post(creator=request.user, post_text=p)
        mynewpost.save()
    return HttpResponseRedirect(reverse("index"))


def update(request, id):
    print(id)
    if request.method == "POST":
        edit = request.POST['edit']
        post = Post.objects.get(id=id)
        post.post_text = edit
        post.save()
    return HttpResponseRedirect(reverse("index"))


def profile(request, creator):
    followtext = "Follow"
    tofollow = User.objects.get(username=creator)
    myfollower = request.user.username
    if Followers.objects.filter(follower=request.user,
                                followee=tofollow).exists():
        followtext = "Unfollow"
    user = User.objects.get(username=creator)
    username = request.user.username
    posts = Post.objects.filter(creator=user)
    posts = posts.order_by("-date")
    # max = bids.objects.filter(listing__id=listing_id).aggregate(Max('bid'))

    #paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    followers = Followers.objects.filter(followee=user).count()
    following = Followers.objects.filter(follower=user).count()
    return render(
        request,
        "network/profile.html",
        {
            "username": username,
            "profile": user,
            "posts": posts,
            "followers": followers,
            "following": following,
            "followtext": followtext,
            "page_obj": page_obj
        },
    )


@login_required(redirect_field_name="", login_url="/login")
def followingpage(request):
    user = User.objects.get(username=request.user.username)
    followers = Followers.objects.filter(follower=request.user).values_list(
        "followee", flat=True)

    print(followers)
    users = User.objects.filter(id__in=followers)
    print(users)
    posts = Post.objects.filter(creator__in=users)
    posts = posts.order_by("-date")

    #paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/followingpage.html", {
        "profile": user,
        "posts": posts,
        "page_obj": page_obj
    })


def follow(request, user):
    tofollow = User.objects.get(username=user)
    myfollower = request.user.username
    if Followers.objects.filter(follower=request.user,
                                followee=tofollow).exists():
        print("already exists")
        Followers.objects.get(follower=request.user,
                              followee=tofollow).delete()
    elif user == myfollower:
        print("they're the same")
    else:
        newfollow = Followers(follower=request.user, followee=tofollow)
        newfollow.save()
    return HttpResponseRedirect(reverse("profile", args=(user, )))


def getpostsall(request):
    posts = Post.objects.all()
    posts = posts.order_by("-date")
    return JsonResponse([post.serialize() for post in posts], safe=False)


@login_required(redirect_field_name="", login_url="/login")
def like(request, postid):
    post = Post.objects.get(id=postid)
    user = request.user
    if Likes.objects.filter(user=request.user, post=post).exists():
        Likes.objects.filter(user=request.user, post=post).delete()
        if post.likes > 0:
            post.likes = post.likes - 1
            post.save()
    else:
        newlike = Likes(user=request.user, post=post)
        newlike.save()
        post.likes = post.likes + 1
        post.save()
    # likecount = Likes.objects.filter(id=postid).count()
    return JsonResponse(post.serialize())


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
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(request, "network/register.html",
                          {"message": "Passwords must match."})

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html",
                          {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
