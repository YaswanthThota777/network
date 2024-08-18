from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User,Post,Follow,Comment
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Post  # Assuming you have a Post model

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Post, Follow, Comment
from django.core.paginator import Paginator

def index(request):
    if request.method == "POST":
        content = request.POST.get("post")
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect("index")
    
    posts = Post.objects.all().order_by('-timestamp')

    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add an attribute to each post to check if the user has liked it
    for post in page_obj:
        post.user_has_liked = post.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False

    context = {
        'posts': page_obj,
    }
    return render(request, 'network/index.html', context)

def all_posts(request):
    if request.method == "POST":
        content = request.POST.get("post")
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect("all_posts")
    
    posts = Post.objects.all().order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
    }
    return render(request, 'network/all_posts.html', context)

@login_required
def following_posts(request):
    user = request.user

    # Get the users that the current user is following
    following_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)

    # Get posts from users that the current user follows
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
    }
    return render(request, 'network/following_posts.html', context)

# Other view functions (login_view, logout_view, register, profile, toggle_like, etc.) remain unchanged.



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


@login_required
def all_posts(request):
    if request.method == "POST":
        content = request.POST.get("post")
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect("all_posts")
    posts = Post.objects.all().order_by('-timestamp')
    context = {
        'posts' : posts,
    }
    return render(request, 'network/all_posts.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user)
    isfollowing = Follow.objects.filter(follower=request.user, followed=user).exists()
    followers_count = Follow.objects.filter(followed=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    context = {
        'username': user,
        'posts': posts,
        'isfollowing': isfollowing,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'network/profile.html', context)


def follow_status(request, username):
    user_to_check = get_object_or_404(User, username=username)
    is_following = request.user in user_to_check.followers.all()
    followers_count = user_to_check.followers.count()

    return JsonResponse({
        'success': True,
        'following': is_following,
        'followers_count': followers_count,
    })



@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count
        })
    return JsonResponse({'success': False}, status=400)


@login_required
def follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.method == 'POST':
        Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
        followers_count = Follow.objects.filter(followed=user_to_follow).count()
        return JsonResponse({
            'success': True,
            'following': True,
            'followers_count': followers_count,
        })
    elif request.method == 'DELETE':
        Follow.objects.filter(follower=request.user, followed=user_to_follow).delete()
        followers_count = Follow.objects.filter(followed=user_to_follow).count()
        return JsonResponse({
            'success': True,
            'following': False,
            'followers_count': followers_count,
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def edit_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id, user=request.user)
        content = request.POST.get("content")
        if content:
            post.content = content
            post.save()
            return JsonResponse({"success": True, "new_content": post.content})
    return JsonResponse({"success": False})


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("comment")

        if content:
            Comment.objects.create(user=request.user, post=post, content=content)

        return redirect("index")


@login_required
def following_posts(request):
    user = request.user

    # Get the users that the current user is following
    following_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)

    # Get posts from users that the current user follows
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')

    context = {
        'posts': posts,
    }
    return render(request, 'network/following_posts.html', context)
