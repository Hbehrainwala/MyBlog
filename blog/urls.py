from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from . import views
from blog.views import CreatePostView, ShowPostView, IndexView, UserUpdateView, MyPostView, \
UpdatePostView, MyPublishPostView, MyUnPublishPostView, MyArchivePostView, DeletePostView, \
MakePostPublishView, MakePostUnpublishView, MakePostArchieveView, NotificationView

urlpatterns = [
  url(r'^$',IndexView.as_view(), name = 'index'),
  url(r'^createpost$',login_required(CreatePostView.as_view()), name = 'createpost'),
  url(r'^success/$', login_required(TemplateView.as_view(template_name="blog/success.html")), name = 'success'),
  url(r'^update$',login_required(UserUpdateView.as_view()), name = 'update'),
  url(r'^mypost$',login_required(MyPostView.as_view()), name = 'mypost'),
  url(r'^updatepost/(?P<slug>[\w\-]+)/$',login_required(UpdatePostView.as_view()), name='updatepost'),
  url(r'^mypublishpost/$', login_required(MyPublishPostView.as_view()), name='mypublishpost'),
  url(r'^myunpublishpost/$', login_required(MyUnPublishPostView.as_view()), name='myunpublishpost'),
  url(r'^myarchivepost/$', login_required(MyArchivePostView.as_view()), name='myarchivepost'),
  url(r'^publishpost/(?P<slug>[\w\-]+)/$',login_required(MakePostPublishView.as_view()), name='publishpost'),
  url(r'^unpublishpost/(?P<slug>[\w\-]+)/$',login_required(MakePostUnpublishView.as_view()), name='unpublishpost'),
  url(r'^archivepost/(?P<slug>[\w\-]+)/$', login_required(MakePostArchieveView.as_view()), name='archivepost'),

  # url(r'^deletepost/(?P<slug>[\w\-]+)/$',login_required(DeletePostView.as_view()), name='deletepost'),
  url(r'^deletepost/(?P<slug>[\w\-]+)/$',views.delete_post_view, name='deletepost'),


  url(r'^createcomment/(?P<slug>[\w\-]+)/$', views.create_comment_view, name='createcomment'),
  url(r'^viewpost/(?P<slug>[\w\-]+)/likepost/$', views.like_post_view, name='likepost'),
  url(r'^viewpost/(?P<slug>[\w\-]+)/likecomment/(?P<c_id>[0-9]+)/$', views.like_comment_view, name='likecomment'),
  url(r'^commentonmypost/(?P<slug>[\w\-]+)/$', views.comments_on_my_post_view, name='commentonmypost'),
  # url(r'^commentonmypost/(?P<slug>[\w\-]+)/$', CommentOnMyPostView.as_view(), name='commentonmypost'),


  url(r'^deletecomment/(?P<c_id>[0-9]+)/$', views.delete_comment_view, name='deletecomment'),


  url(r'^viewpost/(?P<slug>[\w\-]+)/$', ShowPostView.as_view(), name='viewpost'),
  url(r'^becomeblogger/$', views.become_blogger_view, name='becomeblogger'),
  url(r'^notifications/$', NotificationView.as_view(), name='notifications'),


  url(r'^paginateupper/$', views.ajax_upper_paginate_view, name='paginateupper'),
  url(r'^paginatemiddle/$', views.ajax_middle_paginate_view, name='paginatemiddle'),
  url(r'^paginatelower/$', views.ajax_lower_paginate_view, name='paginatelower'),
  url(r'^searchpost/$', views.search_post_view, name='searchpost'),
  url(r'^searchpostajax/$', views.search_post_ajax_view, name='searchpostajax'),
  
  # url(r'^showallcomments/(?P<c_id>[0-9]+)/$', views.show_all_comments_view, name='showallcomment'),
  # url(r'^mostviewedpost/$', views.most_viewed_post_view, name='mostviewedpost'),
  # url(r'^mostlikedpost/$', views.most_liked_post_view, name='mostlikedpost'),


]