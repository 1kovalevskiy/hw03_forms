from .forms import PostForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Group, Post, User
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'index.html',
                  {'page': page, }
                  )


# view-функция для страницы сообщества
def group_posts(request, slug):
    """
    функция get_object_or_404 получает по заданным критериям объект из базы
    данных или возвращает сообщение об ошибке, если объект не найден
    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления условия WHERE group_id = {group_id}
    # posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "page": page})


# view-функция со списком сообществ
@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, "groups_list.html", {"groups": groups})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()

    paginator = Paginator(post_list, 10)
    post_count = paginator.count

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    content = {
        "user_profile": user,
        "page": page,
        "post_count": post_count
    }
    return render(request, 'profile.html', content)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = get_object_or_404(User, username=username)
    post2 = Post.objects.get(pk=post_id)
    if str(post2.author) != str(username):
        return redirect("/")
    post = user.posts.get(pk=post_id)
    post_count = Post.objects.filter(author=user).count
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
            Post.objects.create(author=request.user,
                                text=form.cleaned_data['text'],
                                group=form.cleaned_data['group'])
            return redirect("/")
        else:
            print(form.errors)
        return render(request, "new_post.html", {"form": form})
    form = PostForm()
    return render(request, "new_post.html", {"form": form})


@login_required
def post_edit(request, username, post_id):
    if str(request.user) != str(username):
        return redirect("/")
    post2 = Post.objects.get(pk=post_id)
    if str(post2.author) != str(username):
        return redirect("/")
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect(f"/{username}/{post_id}")
        else:
            print(form.errors)
        # если условие if form.is_valid() ложно и данные не прошли валидацию -
        # передадим полученный объект в шаблон
        # чтобы показать пользователю информацию об ошибке
        # заодно заполним прошедшими валидацию данными все поля,
        # чтобы не заставлять пользователя вносить их повторно
        return render(request, "post_edit.html", {"form": form})

    # если пришёл не POST-запрос - создаём и передаём в шаблон пустую форму
    # пусть пользователь напишет что-нибудь
    form = PostForm(instance=post)
    return render(request, "post_edit.html", {"form": form})
