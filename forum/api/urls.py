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
 (r'thread/list$',              'thread_list'),
 (r'thread/listPosts$',         'thread_listPosts'),
 (r'thread/open$',              'thread_open'),
 (r'thread/remove$',            'thread_remove'),
 (r'thread/restore$',           'thread_restore'),
 (r'thread/subscribe$',         'thread_subscribe'),
 (r'thread/unsubscribe$',       'thread_unsubscribe'),
 (r'thread/update$',            'thread_update'),
 (r'thread/vote$',              'thread_vote'),


 (r'post/create$',              'post_create'),
 (r'post/details$',             'post_details'),

)
