
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("allposts",views.all_posts, name="all_posts"),
    path('profile/<str:username>/',views.profile, name="profile"),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
    path("toggle_like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path('following/', views.following_posts, name='following_posts'),
]

