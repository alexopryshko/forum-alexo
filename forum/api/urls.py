__author__ = 'alexander'

from django.conf.urls import *

urlpatterns = patterns('api.views',

 (r'user/create$',              'user_create'),
 (r'user/details$',             'user_details'),
 (r'user/follow$',              'user_follow'),
 (r'user/listFollowers$',       'user_listFollowers'),
 (r'user/listFollowing$',       'user_listFollowing'),
 (r'user/unfollow$',            'user_unfollow'),
 (r'user/updateProfile$',       'user_updateProfile'),

 (r'forum/create$',             'forum_create'),
 (r'forum/details$',            'forum_details'),
 (r'forum/listUsers$',          'forum_listUsers'),
 (r'forum/listThreads$',        'forum_listThreads'),
 (r'forum/listPosts$',          'forum_listPosts'),

 (r'thread/create$',            'thread_create'),

 (r'post/create$',              'post_create'),



 #(r'^news/new/$', 'ask.views.news_new'),
 #(r'^question/rating/$', 'ask.views.question_popular'),
 #(r'login/$', 'ask.views.login'),
 #(r'logout/$','ask.views.logout'),
 #(r'^tegs/','ask.views.tegs'),
 #(r'^question/([0-9]+)/$', 'ask.views.questionPage'),
 #(r'^question/([0-9]+)/answer/$', 'ask.views.answer'),
 #(r'^question/([0-9]+)/commentq/', 'ask.views.commentq'),
 ##(r'^question/([0-9]+)/commenta/([0-9]+)', 'ask.views.commenta'),
 #(r'^question/like/([0-9]+)','ask.views.likeQ'),
 #(r'^question/dislike/([0-9]+)','ask.views.dislikeQ'),
)
