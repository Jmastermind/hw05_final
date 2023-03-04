from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


def index(request: HttpRequest) -> HttpResponse:
    """Создаёт главную страницу.

    Args:
        request: Запрос на рендер страницы.

    Returns:
        HTML-код страницы.
    """
    posts = Post.objects.select_related('author', 'group')
    page = paginate(request, posts, settings.PAGINATION)

    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page,
            'posts': posts,
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Создаёт страницу группы записей.

    Args:
        request: Запрос на рендер страницы.
        slug: Строка со slug'ом текущей группы записей.

    Returns:
        HTML-код страницы.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page = paginate(request, posts, settings.PAGINATION)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page,
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Создаёт страницу профиля автора.

    Args:
        request: Запрос на рендер страницы.
        username: Строка c никнеймом автора.

    Returns:
        HTML-код страницы.
    """
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    page = paginate(request, posts, settings.PAGINATION)
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': page,
            'following': following,
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Создаёт страницу записи.

    Args:
        request: Запрос на рендер страницы.
        pk: Идентификатор поста.

    Returns:
        HTML-код страницы.
    """
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('author')
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': get_object_or_404(Post, pk=pk),
            'form': CommentForm(request.POST or None),
            'comments': comments,
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Создаёт страницу создания новой записи.

    Args:
        request: Запрос на рендер страницы.

    Returns:
        HTML-код страницы.
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'btn_txt': 'Добавить'},
        )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user)


@login_required
def post_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаляет запись из БД.

    Args:
        request: Запрос http.
        pk: Идентификатор записи.

    Returns:
        Перенаправляет на главную страницу.
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    post.image.delete()
    post.delete()
    return redirect('posts:index')


@login_required
def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Создаёт страницу редактирования записи.

    Args:
        request: Запрос http.
        pk: Идентификатор записи.

    Returns:
        Перенаправляет на страницу записи.
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
        )
        if not form.is_valid():
            return render(
                request,
                'posts/create_post.html',
                {'form': form, 'btn_txt': 'Сохранить'},
            )
        form.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.instance.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    page = paginate(
        request,
        Post.objects.filter(
            author__following__user=request.user,
        ).select_related('author', 'group'),
        settings.PAGINATION,
    )
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': page,
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    if (
        not request.user.follower.filter(author__username=username).exists()
        and username != request.user.username
    ):
        Follow.objects.create(
            user=request.user,
            author=get_object_or_404(User, username=username),
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username,
    ).delete()
    return redirect('posts:profile', username)
