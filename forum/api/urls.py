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
 (r'thread/close$',             'thread_close'),
 (r'thread/details$',           'thread_details'),


 (r'post/create$',              'post_create'),

)
