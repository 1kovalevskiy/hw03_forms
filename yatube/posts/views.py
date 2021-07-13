from .forms import PostForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Group, Post, User
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'index.html',
                  {'page': page, }
                  )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, "groups_list.html", {"groups": groups})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    paginator = Paginator(post_list, 10)
    post_count = paginator.count
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    content = {
        "user_profile": user,
        "page": page,
        "post_count": post_count
    }
    return render(request, 'profile.html', content)


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=user)
    post_count = user.posts.count
    content = {
        "user_post": user,
        "post": post,
        "post_count": post_count
    }
    return render(request, 'post.html', content)


def users_list(request):
    users = User.objects.all()
    return render(request, "users_list.html", {"users": users})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            print(post.pk)
            return redirect(f"/{post.author}/{post.pk}/")
        return render(request, "new_post.html", {"form": form})
    form = PostForm()
    return render(request, "new_post.html", {"form": form})


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=user, pk=post_id)
    if request.user != user:
        return redirect("/")
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect(f"/{username}/{post_id}")
        return render(request, "post_edit.html", {"form": form})
    form = PostForm(instance=post)
    return render(request, "post_edit.html", {"form": form})
