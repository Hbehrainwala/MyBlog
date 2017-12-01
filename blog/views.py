import datetime
import json
from datetime import date

from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, FormView

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
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy

from .models import Post, Profile, Comment, PostLike, CommentLike, Search
from .forms import CreatePostForm, UpdateUserForm, UpdatePostForm, CommentForm, \
NotificationForm, SearchForm
from .mixins import PaginationMixin

  
class IndexView(ListView):
    model = Post
    template_name = 'blog/homepage.html'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        context['latest_posts'] = Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-published')
        paginator = Paginator(context['latest_posts'], 3)
        page = self.request.GET.get('page')
      
        try:
            context['latest_posts'] = paginator.page(page)
        except PageNotAnInteger:
            context['latest_posts'] = paginator.page(1)
        except EmptyPage:
            context['latest_posts'] = paginator.page(paginator.num_pages)

        context['latest_posts_likes']=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-likes')
        paginator = Paginator(context['latest_posts_likes'], 3)
        page = self.request.GET.get('page')
      
        try:
            context['latest_posts_likes'] = paginator.page(page)
        except PageNotAnInteger:
            context['latest_posts_likes'] = paginator.page(1)
        except EmptyPage:
            context['latest_posts_likes'] = paginator.page(paginator.num_pages)


        context['latest_posts_views']=Post.objects.filter(publish=True, published__lte=datetime.datetime.now(), archive=False).order_by('-views')
        paginator = Paginator(context['latest_posts_views'], 3)
        page = self.request.GET.get('page')
      
        try:
            context['latest_posts_views'] = paginator.page(page)
        except PageNotAnInteger:
            context['latest_posts_views'] = paginator.page(1)
        except EmptyPage:
            context['latest_posts_views'] = paginator.page(paginator.num_pages)

        context['searchform'] = self.form_class
        return context


class CreatePostView(View):
    form_class = CreatePostForm
    template_name = 'blog/createpost.html'


    def get(self, request):
        form = self.form_class()
        searchform = SearchForm()
        return render(request, self.template_name, {
            "form" : form, 
            "searchform" : searchform 
            })

    def post(self, request):
        form = self.form_class(request.POST)
        searchform = SearchForm()
        if form.is_valid():
            f=form.save()
            f.user = request.user
            f.save()
            return HttpResponseRedirect(reverse('blog:success'))

        return render(request, self.template_name, {
            "form" : form, 
            "searchform" : searchform 
            })


class UserUpdateView(UpdateView):
    form_class = UpdateUserForm
    template_name = 'blog/updateinfo.html'
    success_url = reverse_lazy('blog:index') 

    def get_object(self):
        return User.objects.get(id=self.request.user.id)



class MyPostView(PaginationMixin, ListView):
    template_name = 'blog/mypost.html'

    def get_context_data(self, **kwargs):
        context = super(MyPostView, self).get_context_data(**kwargs)
        context['cur_date'] = timezone.now
        context['title'] = 'MyPost'
        return context

    def get_queryset(self):
        return self.request.user.post_set.filter(archive=False).order_by('-created')



class UpdatePostView(UpdateView):
    form_class = UpdatePostForm
    template_name = 'blog/updatepost.html'
    success_url = reverse_lazy('blog:mypost')

    def get_object(self, queryset=None):
        return Post.objects.get(slug=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        if self.obj.user != request.user:
            raise PermissionDenied
        return super(UpdatePostView, self).dispatch(request, *args, **kwargs)


class DeletePostView(View):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        post.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class MakePostPublishView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, slug=kwargs['slug'])
        post.publish = True
        post.published = timezone.now() 
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class MakePostUnpublishView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, slug=kwargs['slug'])
        post.publish = False
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  
class CreateCommentView(FormView):
    template_name = 'blog/createcomment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super(CreateCommentView, self).get_context_data(**kwargs)
        context['instance'] = Post.objects.get(slug = self.kwargs['slug'])
        return context

    def form_valid(self, form):
        instance = get_object_or_404(Post, slug=self.kwargs['slug'])
        if instance.user.profile.notify:
            user = User.objects.get(id=self.request.user.id)
            sender = instance.user.email  
            email = EmailMessage('Notification For Comment', "User "+user.username+" Commented on Your Post " , to=[sender])
            email.send()
        f = form.save(commit=False)
        f.posts = instance
        f.author = self.request.user
        f.save()
        return super(CreateCommentView, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:viewpost', kwargs={'slug': self.kwargs['slug']})


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

 
class CommentOnMyPostView(ListView):
    template_name = 'blog/mypostcomment.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(CommentOnMyPostView, self).get_context_data(**kwargs)
        context['post'] = Post.objects.get(slug=self.kwargs['slug'])
        return context

    def get_queryset(self):
        return Post.objects.get(slug=self.kwargs['slug']).comment_set.all()

class DeleteCommentView(View):

    def get(self,request, c_id):
        comment = get_object_or_404(Comment, id=c_id)
        comment.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class MyPublishPostView(PaginationMixin, ListView):
    template_name = 'blog/mypost.html'

    def get_queryset(self):
        return self.request.user.post_set.filter(
            publish = True, 
            published__lte=datetime.datetime.now(), 
            archive=False
            ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(MyPublishPostView, self).get_context_data(**kwargs)
        context['cur_date'] = timezone.now
        context['title'] = 'MyPublishPost'
        return context


class MyUnPublishPostView(PaginationMixin, ListView):
    template_name = 'blog/mypost.html'

    def get_queryset(self):
        return self.request.user.post_set.filter(
            Q(archive=False),
            Q(publish = False)|Q(published__gte = datetime.datetime.now())
            ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(MyUnPublishPostView, self).get_context_data(**kwargs)
        context['cur_date'] = timezone.now
        context['title'] = 'MyUnPublishPost'
        return context


class MyArchivePostView(PaginationMixin, ListView):
    template_name = 'blog/myarchivepost.html'

    def get_queryset(self):
        return self.request.user.post_set.filter(archive = True).order_by('-archive_date')

    def get_context_data(self, **kwargs):
        context = super(MyArchivePostView, self).get_context_data(**kwargs)
        context['cur_date'] = timezone.now
        context['title'] = 'MyArchivePost'
        return context


class MakePostArchieveView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post,slug = kwargs['slug'])
        post.archive = True
        post.archive_date = timezone.now()
        post.save() 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))        


class ShowPostView(DetailView):
    template_name = 'blog/viewpost.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super(ShowPostView, self).get_context_data(**kwargs)
        self.object.views += 1
        self.object.save()
        context['comments'] = self.object.comment_set.all()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(context['comments'], 3)
        try:
            context['comments'] = paginator.page(page)
        except PageNotAnInteger:
            context['comments'] = paginator.page(1)
        except EmptyPage:
            context['comments'] = paginator.page(paginator.num_pages)

        return context


class BecomeBloggerView(View):
    def get(self, request, *args, **kwargs):
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


  
class NotificationView(UpdateView):
    form_class = NotificationForm
    template_name = 'blog/notifyuser.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)


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