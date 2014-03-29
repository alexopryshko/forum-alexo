from django.http import HttpResponse
import json
from db_service.post_db import *
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie

__author__ = 'alexander'

def error():
    result = {'code': 1, 'message': 'error'}
    return result

def success(result):
    answer = {'code': 0, 'response': result}
    return answer

def user_create(request):
    try:
        username = request.POST['username']
        about = request.POST['about']
        isAnonymous = request.POST['isAnonymous']
        name = request.POST['name']
        email = request.POST['email']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if add_user(username, email, name, isAnonymous, about) == False:
        result = user_table(email)
        about = result[0][5]
        email = result[0][2]
        id = result[0][0]
        isAnonymous = result[0][4]
        name = result[0][3]
        username = result[0][2]
    else:
        id = get_user_id_by_email(email)
    result = {'about': about,
              'email': email,
              'id': id,
              'isAnonymous': isAnonymous,
              'name': name,
              'username': username
    }
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def user_details(request):
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = user_info(email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def user_follow(request):
    try:
       follower = request.POST['follower']
       followee = request.POST['followee']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if follower == followee:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = subscribe(follower, followee)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def user_unfollow(request):
    try:
       follower = request.POST['follower']
       followee = request.POST['followee']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if follower == followee:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = unsubscribe(follower, followee)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def user_listFollowers(request):
    order = request.GET.get('order', 'desc')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = list_followers(limit, order, since_id, email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    answer = [user_info(row) for row in result]
    return HttpResponse(json.dumps(success(answer)), content_type='application/json')

def user_listFollowing(request):
    order = request.GET.get('order', 'desc')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = list_following(limit, order, since_id, email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    answer = [user_info(row) for row in result]
    return HttpResponse(json.dumps(success(answer)), content_type='application/json')

def user_updateProfile(request):
    try:
        about = request.POST['about']
        email = request.POST['user']
        name = request.POST['name']
    except MultiValueDictKeyError:
       return HttpResponse(json.dumps(error()), content_type='application/json')
    result = update(name, about, email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def forum_create(request):
    try:
        name = request.POST['name']
        short_name = request.POST['short_name']
        email = request.POST['user']
    except MultiValueDictKeyError:
       return HttpResponse(json.dumps(error()), content_type='application/json')
    user_id = get_user_id_by_email(email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if add_forum(name, short_name, user_id) is False:
        forum = forum_table(short_name)
        result = {'id':         forum[0][0],
                  'name':       forum[0][1],
                  'short_name': forum[0][2],
                  'user':       get_user_email_by_id(forum[0][3])
        }
    else:
        forum_id = get_forum_id(short_name)
        result = {'id':         forum_id,
                  'name':       name,
                  'short_name': short_name,
                  'user':       email
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
    result = forum_info(short_name, include_user)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def forum_listUsers(request):
    order = request.GET.get('order', 'desc')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    users = list_users(limit, order, since_id, short_name)
    if users is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [user_info(user) for user in users]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def forum_listThreads(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    include_user = False
    include_forum = False
    if 'user' in related:
        include_user = True
    if 'forum' in related:
        include_forum = True
    threads = list_thread(limit, order, since_id, short_name)
    if threads is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [thread_info(thread, short_name, include_forum, include_user) for thread in threads]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def forum_listPosts(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
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
    posts = list_post(limit, order, since_id, short_name)
    if posts is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [post_info(post, include_user, include_forum, include_thread) for post in posts]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_create(request):
    is_deleted = request.POST.get('isDeleted', False)
    try:
        short_name = request.POST['forum']
        title = request.POST['title']
        is_closed = request.POST['isClosed']
        email = request.POST['user']
        date = request.POST['date']
        message = request.POST['message']
        slug = request.POST['slug']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = get_user_id_by_email(email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    forum_id = get_forum_id(short_name)
    if forum_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if add_thread(title, message, slug, is_closed, is_deleted, date, forum_id, user_id) is True:
        id = get_thread_id(slug)
        result = {'date':       date,
                  'forum':      short_name,
                  'id':         id,
                  'isClosed':   is_closed,
                  'isDeleted':  is_deleted,
                  'message':    message,
                  'slug':       slug,
                  'title':      title,
                  'user':       email
        }
    else:
        thread = thread_info(id, short_name, False, False)
        result = {'date':       thread['date'],
                  'forum':      thread['forum'],
                  'id':         thread['id'],
                  'isClosed':   thread['isClosed'],
                  'isDeleted':  thread['isDeleted'],
                  'message':    thread['message'],
                  'slug':       thread['slug'],
                  'title':      thread['title'],
                  'user':       thread['user']
        }
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_close(request):
    try:
        thread_id = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if mark_as_closed(thread_id) is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    return HttpResponse(json.dumps(success(thread_id)), content_type='application/json')

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
    short_name = forum_thread(thread_id)
    if short_name is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = thread_info(thread_id, forum_thread(thread_id), include_user, include_forum)
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_list(request):
    order = request.GET.get('order', 'desc')
    email = request.GET.get('user', None)
    short_name = request.GET.get('forum', None)
    try:
        since = request.GET['since']
        limit = request.GET['limit']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if email is None:
        threads = list_thread(limit, order, since, short_name)
        if threads is None:
            return HttpResponse(json.dumps(error()), content_type='application/json')
        result = [thread_info(thread, short_name, False, False) for thread in threads]
        return HttpResponse(json.dumps(success(result)), content_type='application/json')
    else:
        threads = thread_created_by_user(email, since, order, limit)
        if threads is None:
            return HttpResponse(json.dumps(error()), content_type='application/json')
        result = [thread_info(thread, forum_thread(thread), False, False) for thread in threads]
        return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_listPosts(request):
    order = request.GET.get('order', 'desc')
    since = request.GET['since']  # replace this code
    limit = request.GET['limit']
    try:
        thread = request.GET['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    posts = list_thread_posts(thread, since, order, limit)
    result = [post_info(post, False, False, False) for post in posts]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_open(request):
    try:
        thread = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread_id = mark_as_open(thread)
    if thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_remove(request):
    try:
        thread = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread_id = mark_as_deleted(thread)
    if thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_restore(request):
    try:
        thread = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread_id = mark_as_restored(thread)
    if thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

@ensure_csrf_cookie
def thread_subscribe(request):
    try:
        email = request.POST['user']
        thread_id = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if subscribe_to_thread(thread_id, email) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id, 'user': email}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

@ensure_csrf_cookie
def thread_unsubscribe(request):
    try:
        email = request.POST['user']
        thread_id = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if unsubscribe_to_thread(thread_id, email) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id, 'user': email}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

def thread_update(request):
    try:
        message = request.POST['message']
        slug = request.POST['slug']
        thread_id = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if update_thread(thread_id, message, slug) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(thread_info(thread_id, forum_thread(thread_id), False, False))), content_type='application/json')

def thread_vote(request):
    try:
        vote = request.POST['vote']
        thread_id = request.POST['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    like = 0
    dislike = 0
    if vote == 1:
        like = 1
    else:
        dislike = 1
    point = like - dislike
    if vote_thread(thread_id, like, dislike, point) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(thread_info(thread_id, forum_thread(thread_id), False, False))),
                        content_type='application/json')


def post_create(request):
    parent = request.POST.get('parent', None)
    is_approved = request.POST.get('isApproved', False)
    is_highlighted = request.POST.get('isHighlighted',False)
    is_edited = request.POST.get('isEdited',False)
    is_spam = request.POST.get('isSpam', False)
    is_deleted = request.POST.get('isDeleted', False)

    try:
        date = request.POST['date']
        thread_id = request.POST['thread']
        message = request.POST['message']
        email = request.POST['user']
        short_name = request.POST['forum']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = get_user_id_by_email(email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    slug = get_thread_slug(thread_id)
    if slug is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    post_id = add_post(message, is_approved, is_highlighted, is_edited,
                       is_spam, is_deleted, date, thread_id, user_id, parent)
    result = {'date':           date,
              'forum':          short_name,
              'id':             post_id,
              'isApproved':     is_approved,
              'isDeleted':      is_deleted,
              'isEdited':       is_edited,
              'isHighlighted':  is_highlighted,
              'isSpam':         is_spam,
              'message':        message,
              'thread':         thread_id,
              'user':           email
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

    result = post_info(post_id, include_user, include_forum, include_thread)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')

