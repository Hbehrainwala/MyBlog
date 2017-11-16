from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$',views.index, name = 'index'),
  url(r'^createpost$',views.create_post_view, name = 'createpost'),
  url(r'^update$',views.user_update_view, name = 'update'),
  url(r'^mypost$',views.my_post_view, name = 'mypost'),
  url(r'^updatepost/(?P<slug>[\w\-]+)/$',views.update_post_view, name='updatepost'),
  url(r'^deletepost/(?P<c_id>[0-9]+)/$',views.delete_post_view, name='deletepost'),
  url(r'^publishpost/(?P<c_id>[0-9]+)/$',views.publish_post_view, name='publishpost'),
  url(r'^unpublishpost/(?P<c_id>[0-9]+)/$',views.unpublish_post_view, name='unpublishpost'),
  url(r'^createcomment/(?P<slug>[\w\-]+)/$', views.create_comment_view, name='createcomment'),
  url(r'^viewpost/(?P<slug>[\w\-]+)/likepost/$', views.like_post_view, name='likepost'),
  url(r'^archivepost/(?P<slug>[\w\-]+)/$', views.archive_post_view, name='archivepost'),
  url(r'^viewpost/(?P<slug>[\w\-]+)/likecomment/(?P<c_id>[0-9]+)/$', views.like_comment_view, name='likecomment'),
  # url(r'^showallcomments/(?P<c_id>[0-9]+)/$', views.show_all_comments_view, name='showallcomment'),
  url(r'^commentonmypost/(?P<slug>[\w\-]+)/$', views.comments_on_my_post_view, name='commentonmypost'),
  url(r'^deletecomment/(?P<c_id>[0-9]+)/$', views.delete_comment_view, name='deletecomment'),
  url(r'^mypublishpost/$', views.my_publish_post_view, name='mypublishpost'),
  url(r'^myunpublishpost/$', views.my_unpublish_post_view, name='myunpublishpost'),
  url(r'^myarchivepost/$', views.my_archive_post_view, name='myarchivepost'),
  url(r'^viewpost/(?P<slug>[\w\-]+)/$', views.view_post_view, name='viewpost'),
  # url(r'^mostviewedpost/$', views.most_viewed_post_view, name='mostviewedpost'),
  # url(r'^mostlikedpost/$', views.most_liked_post_view, name='mostlikedpost'),
  url(r'^becomeblogger/$', views.become_blogger_view, name='becomeblogger'),
  url(r'^notifications/$', views.notifications_view, name='notifications'),
  url(r'^paginateupper/$', views.ajax_upper_paginate_view, name='paginateupper'),
  url(r'^paginatemiddle/$', views.ajax_middle_paginate_view, name='paginatemiddle'),
  url(r'^paginatelower/$', views.ajax_lower_paginate_view, name='paginatelower'),
  url(r'^searchpost/$', views.search_post_view, name='searchpost'),
  url(r'^searchpostajax/$', views.search_post_ajax_view, name='searchpostajax'),


]