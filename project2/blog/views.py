from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template import loader
from . import models
from . import forms
from django.contrib.auth.decorators import login_required
# Create your views here.


def allowed(request, id):
    post = models.Posts.objects.get(id=id)
    if post.author != request.user:
        raise Http404


def home_page(request):
    template = loader.get_template('home_page.html')
    context = {}
    return HttpResponse(template.render(context, request))


@login_required
def post(request):
   # posts = models.Posts.objects.filter(author=request.user).order_by('-created_on')
    posts = models.Posts.objects.order_by('-created_on')
    context = {'posts': posts}
    return render(request, 'posts.html', context)


@login_required
def add_post(request):
    if request.method != 'POST':
        form = forms.PostForm()
    else:
        form = forms.PostForm(request.POST, request.FILES)
        if form.is_valid():
            add_post = form.save(commit=False)
            add_post.author = request.user
            add_post.save()
            return redirect('blog:posts')
    context = {'form': form}
    return render(request, 'add_post.html', context)


@login_required
def update_post(request, post_id):
    allowed(request, post_id)
    post = models.Posts.objects.get(id=post_id)
    if request.method != 'POST':
        form = forms.UpdateForm(instance=post)
    else:
        form = forms.UpdateForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:posts')
    context = {'post': post, 'form': form}
    template = loader.get_template('update_post.html')
    return HttpResponse(template.render(context, request))


@login_required
def comment(request, post_id):
    post = models.Posts.objects.get(id=post_id)
    comments = post.comments_set.order_by('-created_on')
    context = {'comments': comments, 'post': post}
    return render(request, 'comment.html', context)


@login_required
def submit_comment(request, post_id):
    post = models.Posts.objects.get(id=post_id)
    comment = post.comments_set.order_by('-created_on')
    if request.method != 'POST':
        form = forms.CommentsForm()
    else:
        form = forms.CommentsForm(data=request.POST)
        if form.is_valid():
            new_c = form.save(commit=False)
            new_c.post = post
            new_c.save()
            return redirect('blog:comments', post_id=post.id)
    context = {'post': post, 'comment': comment, 'form': form}
    return render(request, 'submit_comment.html', context)
