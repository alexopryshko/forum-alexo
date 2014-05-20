from django.http import HttpResponse
import json
from api.db_service.user_db import User
from api.db_service.forum_db import Forum
from api.db_service.helper import *
from django.utils.datastructures import MultiValueDictKeyError

__author__ = 'alexander'


def forum_create(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    name = request_data.get('name', None).encode('utf-8')
    try:
        short_name = request_data['short_name'].encode('utf-8')
        email = request_data['user'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    user_id = User.get_inf(False, email=email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    forum = Forum(name=name, short_name=short_name, user=user_id, )
    forum.save()
    result = {
        'id': forum.id,
        'name': forum.name,
        'short_name': forum.short_name,
        'user': User.get_inf(id=forum.user)
    }
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def forum_details(request):
    related = request.GET.get('related', '[]')
    try:
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    include_user = False
    if 'user' in related:
        include_user = True
    result = Forum.get_inf(True, include_user, forum=short_name)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def forum_listUsers(request):
    order = request.GET.get('order', 'desc')
    limit = request.GET.get('limit')
    since_id = request.GET.get('since_id')
    try:
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    users = Forum.list_users(limit, order, since_id, short_name)
    if users is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(users)), content_type='application/json')


def forum_listThreads(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    limit = request.GET.get('limit')
    since = request.GET.get('since')
    try:
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    include_user = False
    include_forum = False
    if 'user' in related:
        include_user = True
    if 'forum' in related:
        include_forum = True
    threads = Forum.list_threads(limit, order, since, short_name, include_user, include_forum)
    if threads is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(threads)), content_type='application/json')


def forum_listPosts(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    limit = request.GET.get('limit')
    since = request.GET.get('since')
    try:
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    include_user = False
    include_forum = False
    include_thread = False
    if 'user' in related:
        include_user = True
    if 'forum' in related:
        include_forum = True
    if 'thread' in related:
        include_thread = True
    posts = Forum.list_posts(limit, order, since, short_name, include_user, include_forum, include_thread)
    if posts is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(posts)), content_type='application/json')