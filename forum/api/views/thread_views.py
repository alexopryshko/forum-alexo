from django.http import HttpResponse
import json
from api.db_service.user_db import User
from api.db_service.forum_db import Forum
from api.db_service.thread_db import Thread
from api.db_service.helper import *
from django.utils.datastructures import MultiValueDictKeyError

__author__ = 'alexander'


def thread_create(request):
    request_data = json.loads(request.body)
    #request_data = request.POST

    is_deleted = string_to_bool(request_data.get('isDeleted'))
    try:
        is_closed = string_to_bool(request_data['isClosed'])
        title = request_data['title'].encode('utf-8')
        message = request_data['message'].encode('utf-8')
        short_name = request_data['forum'].encode('utf-8')
        email = request_data['user'].encode('utf-8')
        date = request_data['date'].encode('utf-8')
        slug = request_data['slug'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = User.get_inf(email=email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    forum_id = Forum.get_inf(forum=short_name)
    if forum_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    thread = Thread(title=title,
                    message=message,
                    slug=slug,
                    is_closed=is_closed,
                    is_deleted=is_deleted,
                    date=date,
                    forum=forum_id,
                    user_id=user_id,
                    user=email)
    if not thread.save():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {
        'date': thread.date,
        'forum': short_name,
        'id': thread.id,
        'isClosed': thread.is_closed,
        'isDeleted': thread.is_deleted,
        'message': thread.message,
        'slug': thread.slug,
        'title': thread.title,
        'user': email
    }
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_close(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread = Thread(is_closed=True, id=thread_id)

    if not thread.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success({'thread': thread_id})), content_type='application/json')


def thread_details(request):
    related = request.GET.get('related', '[]')
    try:
        thread_id = request.GET['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    include_user = False
    include_forum = False
    if 'user' in related:
        include_user = True
    if 'forum' in related:
        include_forum = True
    result = Thread.get_inf(thread_id, include_user, include_forum)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_list(request):
    order = request.GET.get('order', 'desc')
    email = request.GET.get('user', None)
    short_name = request.GET.get('forum', None)
    since = request.GET.get('since')
    limit = request.GET.get('limit')

    if email is not None:
        user_id = User.get_inf(email=email)
        if user_id is None:
            return HttpResponse(json.dumps(error()), content_type='application/json')
        result = Thread.list(since, limit, order, user=user_id)
        return HttpResponse(json.dumps(success(result)), content_type='application/json')
    elif short_name is not None:
        result = Thread.list(since, limit, order, forum=short_name)
        return HttpResponse(json.dumps(success(result)), content_type='application/json')
    else:
        return HttpResponse(json.dumps(error()), content_type='application/json')


def thread_listPosts(request):
    order = request.GET.get('order', 'desc')
    since = request.GET.get('since')
    limit = request.GET.get('limit')
    try:
        thread = request.GET['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = Thread.list_posts(thread, since, limit, order)
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_open(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread = Thread(is_closed=False, id=thread_id)
    if not thread.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success({'thread': thread_id})), content_type='application/json')


def thread_remove(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread = Thread(is_deleted=True, id=thread_id)
    if not thread.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success({'thread': thread_id})), content_type='application/json')


def thread_restore(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread = Thread(is_deleted=False, id=thread_id)
    if not thread.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success({'thread': thread_id})), content_type='application/json')


def thread_subscribe(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        email = request_data['user']
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if not Thread.subscribe(thread_id, email):
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id, 'user': email}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_unsubscribe(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        email = request_data['user']
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if not Thread.unsubscribe(thread_id, email):
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id, 'user': email}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_update(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        message = request_data['message'].encode('utf-8')
        slug = request_data['slug'].encode('utf-8')
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    thread = Thread(message=message, slug=slug, id=thread_id)
    if not thread.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(Thread.get_inf(thread_id))), content_type='application/json')


def thread_vote(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        vote = request_data['vote']
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    like = 0
    dislike = 0
    if int(vote) == 1:
        like = 1
    else:
        dislike = 1
    point = like - dislike
    thread = Thread(likes=like, dislikes=dislike, points=point, id=thread_id)
    if not thread.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(Thread.get_inf(thread_id))), content_type='application/json')