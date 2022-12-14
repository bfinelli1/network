from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost, name="newpost"),
    path("getposts/all", views.getpostsall, name="getpostsall"),
    path("profile/<str:creator>", views.profile, name="profile"),
    path("followingpage", views.followingpage, name="followingpage"),
    path("follow/<str:user>", views.follow, name="follow"),
    path("update/<int:id>", views.update, name="update"),
    path("like/<int:postid>", views.like, name="like"),
]
