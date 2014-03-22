__author__ = 'alexander'

from django.conf.urls import *

urlpatterns = patterns('api.views',

 (r'user/create$', 'user_create'),
 (r'user/details$', 'user_details'),
 (r'user/follow$', 'user_follow'),
 (r'user/listFollowers$', 'user_listFollowers'),

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
