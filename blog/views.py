import datetime
import json
from datetime import date

from django.conf import settings
from django.shortcuts import render, get_object_or_404, Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.module_loading import import_module
from ipware.ip import get_ip
from django.contrib import messages
from django.db.models import Q
from django.core.mail import EmailMessage
from django.core import serializers
from django.template.loader import render_to_string
from django.shortcuts import render_to_response

from .models import Post, Profile, Comment, PostLike, CommentLike, Search
from .forms import CreatePostForm, UpdateUserForm, UpdatePostForm, CommentForm, \
NotificationForm, SearchForm


def index(request):
  
    latest_posts=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-published')
    paginator = Paginator(latest_posts, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts = paginator.page(page)
    except PageNotAnInteger:
        latest_posts = paginator.page(1)
    except EmptyPage:
        latest_posts = paginator.page(paginator.num_pages)

  
    latest_posts_likes=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-likes')
    paginator = Paginator(latest_posts_likes, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts_likes = paginator.page(page)
    except PageNotAnInteger:
        latest_posts_likes = paginator.page(1)
    except EmptyPage:
        latest_posts_likes = paginator.page(paginator.num_pages)

    latest_posts_views=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-views')
    paginator = Paginator(latest_posts_views, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts_views = paginator.page(page)
    except PageNotAnInteger:
        latest_posts_views = paginator.page(1)
    except EmptyPage:
        latest_posts_views = paginator.page(paginator.num_pages)

    searchform = SearchForm() 
    return render(request, 'blog/homepage.html', {
        'searchform':searchform, 
        'latest_posts' : latest_posts, 
        'latest_posts_likes':latest_posts_likes, 
        'latest_posts_views':latest_posts_views
        })
  
  

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            f=form.save()
            f.user = request.user
            f.save()
            return HttpResponseRedirect(reverse('blog:index'))
    else:
        form = CreatePostForm()
        searchform = SearchForm()
        return render(request, 'blog/createpost.html', {
            "form" : form, 
            "searchform" : searchform 
            })


@login_required
def user_update_view(request):
    instance = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        form = UpdateUserForm(data=request.POST, instance=request.user)
        if form.is_valid():
            f = form.save()
            return HttpResponseRedirect(reverse('blog:index'))

    else:
        searchform = SearchForm()
        form = UpdateUserForm(instance=instance)
        return render(request, 'blog/updateinfo.html', {
            "form" : form, 
            "searchform" : searchform
            })


@login_required
def my_post_view(request):
    if request.user.profile.blogger:
        cur_date = timezone.now
        latest_posts =request.user.post_set.filter(archive=False).order_by('-created')
        page = request.GET.get('page', 1)



        paginator = Paginator(latest_posts, 3)
        try:
            latest_posts = paginator.page(page)
        except PageNotAnInteger:
            latest_posts = paginator.page(1)
        except EmptyPage:
            latest_posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/mypost.html', {'latest_posts' : latest_posts,'cur_date':cur_date})

    else:
        return HttpResponseRedirect(reverse('blog:index'))

@login_required
def update_post_view(request,slug):
    if request.user.profile.blogger:
        instance = get_object_or_404(Post, slug=slug)
        if request.method == 'POST':
            form = UpdatePostForm(request.POST, instance=instance)
            if form.is_valid():
                f = form.save()
                return HttpResponseRedirect(reverse('blog:mypost'))

        else:
            form = UpdatePostForm(instance=instance)
            return render(request, 'blog/updatepost.html', {"form" : form})
    else:
        return HttpResponseRedirect(reverse('blog:index'))

@login_required
def delete_post_view(request,c_id):
    post = get_object_or_404(Post, id=c_id)
    post.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def publish_post_view(request,c_id):
    post = get_object_or_404(Post,id=c_id)
    post.publish = True
    post.published = timezone.now() 
    post.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def unpublish_post_view(request,c_id):
    post = get_object_or_404(Post, id = c_id)
    post.publish = False 
    post.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
  
@login_required
def create_comment_view(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.user.profile.notify:
        user = User.objects.get(id=request.user.id)
        sender = instance.user.email  
        email = EmailMessage('Notification For Comment', "User "+user.username+" Commented on Your Post " , to=[sender])
        email.send()


    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            f = form.save()
            f.posts = instance
            f.author = request.user
            f.save()
        return HttpResponseRedirect(reverse('blog:viewpost', kwargs={'slug': slug}))
    
    else:
        form = CommentForm(instance=instance) 
        return render(request, 'blog/createcomment.html', {'form': form, 'instance':instance})

def like_post_view(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated():
        if PostLike.objects.filter(user=request.user, posts = post).exists():
            data = {"message":'You Already Like it',"likes":post.likes}
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            ip = get_ip(request)
            postlike = PostLike.objects.create(ip=ip)
            postlike.user=request.user
            postlike.posts = post
            postlike.save()
            post.likes = post.likes +1
            post.save()
            data = {'message':'You like it' ,"likes":post.likes}
            return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        data = {"message":'You Need to Login First!!!',"likes":post.likes}
        return HttpResponse(json.dumps(data), content_type="application/json")

def like_comment_view(request, slug,c_id):
    comment = get_object_or_404(Comment, id=c_id) 

    if request.user.is_authenticated():
        if CommentLike.objects.filter(user=request.user, comments = comment).exists():
            data = {"message":'You Already Like it',"likes":comment.likes}
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            ip = get_ip(request)
            commentlike = CommentLike.objects.create(ip=ip)
            commentlike.user=request.user
            commentlike.comments = comment
            commentlike.save()
            comment.likes = comment.likes +1
            comment.save()
            data = {'message':'You like it' ,"likes":comment.likes}
            return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        data = {"message":'You Need to Login First!!!',"likes":comment.likes}
        return HttpResponse(json.dumps(data), content_type="application/json")



# def show_all_comments_view(request,c_id):
#   post = get_object_or_404(Post, id=c_id)
#   latest_comment=post.comment_set.all()
#   paginator = Paginator(latest_comment, 5)
#   page = request.GET.get('page')
  
#   try:
#     latest_comment = paginator.page(page)
#   except PageNotAnInteger:
#     latest_comment = paginator.page(1)
#   except EmptyPage:
#     latest_comment = paginator.page(paginator.num_pages)

#   return render(request, 'blog/showallcomment.html', { 'latest_comment' : latest_comment,'post':post})
 
def comments_on_my_post_view(request,slug):
    post = get_object_or_404(Post, slug = slug)
    latest_comment=post.comment_set.all()
    paginator = Paginator(latest_comment, 5)
    page = request.GET.get('page')
  
    try:    
        latest_comment = paginator.page(page)
    except PageNotAnInteger:
        latest_comment = paginator.page(1)
    except EmptyPage:
        latest_comment = paginator.page(paginator.num_pages)

    return render(request, 'blog/mypostcomment.html', { 'latest_comment' : latest_comment,'post':post})

def delete_comment_view(request,c_id):
    comment = get_object_or_404(Comment, id=c_id)
    comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def my_publish_post_view(request):
    if request.user.profile.blogger:
        cur_date = timezone.now
        latest_posts =request.user.post_set.filter(publish = True,published__lte=datetime.datetime.now(),archive=False).order_by('-created')
        page = request.GET.get('page', 1)
        paginator = Paginator(latest_posts, 5)
        try:
            latest_posts = paginator.page(page)
        except PageNotAnInteger:
            latest_posts = paginator.page(1)
        except EmptyPage:
            latest_posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/mypublishpost.html', {'latest_posts' : latest_posts})
    else:
        return HttpResponseRedirect(reverse('blog:index'))


def my_unpublish_post_view(request):
    if request.user.profile.blogger:
        cur_date = timezone.now
        latest_posts =request.user.post_set.filter(Q(archive=False),Q(publish = False)|Q(published__gte = datetime.datetime.now())).order_by('-created')
        page = request.GET.get('page', 1)

        paginator = Paginator(latest_posts, 5)
        try:
            latest_posts = paginator.page(page)
        except PageNotAnInteger:
            latest_posts = paginator.page(1)
        except EmptyPage:
            latest_posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/myunpublishpost.html', {'latest_posts' : latest_posts,'cur_date':cur_date})

    else:
        return HttpResponseRedirect(reverse('blog:index'))


def my_archive_post_view(request):
    if request.user.profile.blogger:
        cur_date = timezone.now
        latest_posts =request.user.post_set.filter(archive = True).order_by('-archive_date')
        page = request.GET.get('page', 1)

        paginator = Paginator(latest_posts, 5)
        try:
            latest_posts = paginator.page(page)
        except PageNotAnInteger:
            latest_posts = paginator.page(1)
        except EmptyPage:
            latest_posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/myarchivepost.html', {'latest_posts' : latest_posts,'cur_date':cur_date})

    else:
        return HttpResponseRedirect(reverse('blog:index'))

def archive_post_view(request,slug):
    post = get_object_or_404(Post,slug = slug)
    post.archive = True
    post.archive_date = timezone.now
    post.save() 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def view_post_view(request,slug):
    post = get_object_or_404(Post, slug = slug)
    post.views = post.views + 1
    post.save()
    comments = post.comment_set.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 3)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    return render(request, 'blog/viewpost.html', {'post':post,'comments':comments})

# def most_viewed_post_view(request):
#   latest_posts=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-views')
#   paginator = Paginator(latest_posts, 5)
#   page = request.GET.get('page')
  
#   try:
#     latest_posts = paginator.page(page)
#   except PageNotAnInteger:
#     latest_posts = paginator.page(1)
#   except EmptyPage:
#     latest_posts = paginator.page(paginator.num_pages)

#   return render(request, 'blog/homepage.html', { 'latest_posts' : latest_posts})

# def most_liked_post_view(request):
#   latest_posts=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-likes')
#   paginator = Paginator(latest_posts, 5)
#   page = request.GET.get('page')
  
#   try:
#     latest_posts = paginator.page(page)
#   except PageNotAnInteger:
#     latest_posts = paginator.page(1)
#   except EmptyPage:
#     latest_posts = paginator.page(paginator.num_pages)

#   return render(request, 'blog/homepage.html', { 'latest_posts' : latest_posts})

def become_blogger_view(request):
    user = User.objects.get(id=request.user.id)
  
    if request.user.profile.request:
        return HttpResponseRedirect(reverse('blog:index'))

    else:
        admin = settings.ADMIN_EMAIL
        user.profile.request = True  
        user.save()
        email = EmailMessage('Request for blogger', "User "+user.username+" wants to become blogger" , to=[admin])
        email.send()
        return HttpResponseRedirect(reverse('blog:index'))

def notifications_view(request):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        form = NotificationForm(request.POST, instance=request.user)
        if form.is_valid():
            f = form.save()
            f.profile.notify = True
            f.profile.save()
            return HttpResponseRedirect(reverse('blog:index'))
    
    else:
        form = NotificationForm() 
        return render(request, 'blog/notifyuser.html', {'form':form})
  

def ajax_upper_paginate_view(request):
    latest_posts = Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-published')
  
    paginator = Paginator(latest_posts, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts = paginator.page(page)
    except PageNotAnInteger:
        latest_posts = paginator.page(1)
    except EmptyPage:
        latest_posts = paginator.page(paginator.num_pages)
  
    html_str = render_to_string("blog/homepage_ajax.html", context={"latest_posts": latest_posts})
    return HttpResponse(html_str)

def ajax_middle_paginate_view(request):
    latest_posts = Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-likes')
  
    paginator = Paginator(latest_posts, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts = paginator.page(page)
    except PageNotAnInteger:
        latest_posts = paginator.page(1)
    except EmptyPage:
        latest_posts = paginator.page(paginator.num_pages)
  
    html_str = render_to_string("blog/homepage_middle.html", context={"latest_posts": latest_posts})
    return HttpResponse(html_str)

def ajax_lower_paginate_view(request):
    latest_posts = Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-views')
  
    paginator = Paginator(latest_posts, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts = paginator.page(page)
    except PageNotAnInteger:
        latest_posts = paginator.page(1)
    except EmptyPage:
        latest_posts = paginator.page(paginator.num_pages)
  
    html_str = render_to_string("blog/homepage_lower.html", context={"latest_posts": latest_posts})
    return HttpResponse(html_str)


def search_post_view(request):
    if 'search' in request.GET and request.GET['search']:
        page = request.GET.get('page', 1)
        search = request.GET['search']
        latest_posts = Post.objects.filter(Q(publish=True,published__lte=datetime.datetime.now(), archive=False),Q(post__icontains = search)|Q(description__icontains = search)).order_by('published')
    
        paginator = Paginator(latest_posts, 3)
        page = request.GET.get('page')
    
        try:
            latest_posts = paginator.page(page)
        except PageNotAnInteger:
            latest_posts = paginator.page(1)
        except EmptyPage:
            latest_posts = paginator.page(paginator.num_pages)
    # else:
    #     # messages.add_message(request, messages.INFO, 'No Searched Post Available!')
    #     data = {"message":'No Search Post Availabel',"status":'401'}
    #     return HttpResponse(json.dumps(data), content_type="application/json")

        searchform = SearchForm() 
        return render_to_response('blog/searchpost.html',
             {'latest_posts': latest_posts, 'searchform': searchform })
    else:
        return render(request, 'blog/searchpost.html')



def search_post_ajax_view(request):
    search = request.GET.get('search')
    latest_posts = Post.objects.filter(Q(publish=True,published__lte=datetime.datetime.now(), archive=False),Q(post__icontains = search)|Q(description__icontains = search)).order_by('published')
    paginator = Paginator(latest_posts, 3)
    page = request.GET.get('page')
  
    try:
        latest_posts = paginator.page(page)
    except PageNotAnInteger:
        latest_posts = paginator.page(1)
    except EmptyPage:
        latest_posts = paginator.page(paginator.num_pages)

    html_str = render_to_string("blog/searchpost_ajax.html", context={"latest_posts": latest_posts})
    return HttpResponse(html_str)













# def search_post_view(request):
#   if request.method == "POST":
#     form = SearchForm(request.POST)
#     if form.is_valid():
#       search_text=form.cleaned_data['search']
   
#   else:
#     search_text = request.GET.get('search')
#     form = SearchForm() 
#     return render(request, 'blog/searchpost.html', {'form':form})
  
#   search=search_text
#   latest_posts = Post.objects.filter(Q(publish=True, published__lte=datetime.datetime.now(), archive=False) & Q(post__icontains=search) | Q(description__icontains=search)).order_by('-published')
  
#   page = request.GET.get('page', 1)
#   paginator = Paginator(latest_posts, 2)
#   try:
#       latest_posts = paginator.page(page)
#   except PageNotAnInteger:
#       latest_posts = paginator.page(1)
#   except EmptyPage:
#       latest_posts = paginator.page(paginator.num_pages)
#   return render(request, 'blog/searchpost.html', {'latest_posts': latest_posts})
#   