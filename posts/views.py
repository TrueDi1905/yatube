from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow

User = get_user_model()


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    paginator = Paginator(group.posts.all()[:12], 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page,
                                          'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:index')
        return render(request, "new_post.html", {'form': form})
    form = PostForm()
    return render(request, "new_post.html", {'form': form})


class JustStaticPage(TemplateView):
    template_name = 'about_author.html'


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = ''
    if request.user.is_authenticated:
        following = Follow.objects.filter(author__following__user=request.user)
    context = {
        'author': author,
        'page': page,
        'post_list': post_list,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'profile.html', context=context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm()
    return render(request, 'post.html', {'post': post, 'author': author,
                                         'comments': comments, 'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.username != post.author.username:
        return redirect('posts:post', username, post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post', post_id=post_id, username=username)
    return render(request, 'new_post.html', {'form': form, 'post': post,
                                             'post_id': post_id, 'username': username})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = get_object_or_404(Post, id=post_id)
            comment.save()
            return redirect('posts:post', post_id=post_id, username=username)
        return render(request, "comments.html", {'form': form})
    form = CommentForm()
    post = get_object_or_404(Post, id=post_id)
    return render(request, "comments.html", {'form': form, 'post_id': post.id, 'username': post.author.username})


@login_required
def follow_index(request):
    follow = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(follow, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    fol = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=fol)
    if follow or request.user.username == username:
        return redirect("/")
    else:
        pod = Follow()
        pod.user = request.user
        pod.author = fol
        pod.save()
    return redirect("/")


@login_required
def profile_unfollow(request, username):
    fol = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(author=fol, user=request.user)
    follow.delete()
    return redirect("/")
