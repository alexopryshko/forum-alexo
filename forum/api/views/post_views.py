from django.http import HttpResponse
import json
from api.db_service.user_db import User
from api.db_service.post_db import Post
from api.db_service.helper import *
from django.utils.datastructures import MultiValueDictKeyError
import string

__author__ = 'alexander'


def post_create(request):
    request_data = json.loads(request.body)
    #request_data = request.POST

    parent = request_data.get('parent', None)
    is_approved = string_to_bool(request_data.get('isApproved'))
    is_highlighted = string_to_bool(request_data.get('isHighlighted'))
    is_edited = string_to_bool(request_data.get('isEdited'))
    is_spam = string_to_bool(request_data.get('isSpam'))
    is_deleted = string_to_bool(request_data.get('isDeleted'))

    try:
        date = request_data['date'].encode('utf-8')
        thread_id = request_data['thread']
        message = request_data['message'].encode('utf-8')
        email = request_data['user'].encode('utf-8')
        short_name = request_data['forum'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = User.get_inf(email=email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    post = Post(message=message,
                is_approved=is_approved,
                is_highlighted=is_highlighted,
                is_edited=is_edited,
                is_spam=is_spam,
                is_deleted=is_deleted,
                date=date,
                thread=thread_id,
                user=user_id,
                forum=short_name,
                parent=parent)
    post.save()
    result = {
        'date': post.date,
        'forum': post.forum,
        'id': post.id,
        'isApproved': post.is_approved,
        'isDeleted': post.is_deleted,
        'isEdited': post.is_edited,
        'isHighlighted': post.is_highlighted,
        'isSpam': post.is_spam,
        'message': post.message,
        'thread': post.thread,
        'user': email
    }
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def post_details(request):
    related = request.GET.get('related', '[]')
    try:
        post_id = request.GET['post']
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
    result = Post.get_inf(post_id, include_user, include_thread, include_forum)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def post_lists(request):
    since = request.GET.get('since')
    limit = request.GET.get('limit')
    order = request.GET.get('order', 'desc')

    short_name = request.GET.get('forum', None)
    thread_id = request.GET.get('thread', None)

    if thread_id is not None:
        result = Post.list_posts(since, limit, order, thread=thread_id)
    elif short_name is not None:
        result = Post.list_posts(since, limit, order, forum=short_name)
    else:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def post_remove(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        post_id = request_data['post']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    post = Post(is_deleted=True, id=post_id)
    if not post.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success({'post': post_id})), content_type='application/json')


def post_restore(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        post_id = request_data['post']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    post = Post(is_deleted=False, id=post_id)
    if not post.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success({'post': post_id})), content_type='application/json')


def post_update(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        post_id = request_data['post']
        message = request_data['message']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    post = Post(message=message, id=post_id)
    if not post.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(Post.get_inf(post_id))), content_type='application/json')


def post_vote(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        post_id = request_data['post']
        vote = request_data['vote']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    like = 0
    dislike = 0
    if int(vote) == 1:
        like = 1
    else:
        dislike = 1
    point = like - dislike
    post = Post(likes=like, dislikes=dislike, points=point, id=post_id)
    if not post.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(Post.get_inf(post_id))), content_type='application/json')