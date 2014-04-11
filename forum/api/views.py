from django.http import HttpResponse
import json
from db_service.post_db import *
from django.utils.datastructures import MultiValueDictKeyError

__author__ = 'alexander'


def error():
    result = {'code': 1, 'message': 'error'}
    return result


def success(result):
    answer = {'code': 0, 'response': result}
    return answer


def user_create(request):
    request_data = json.loads(request.body)

    is_anonymous = request_data.get('isAnonymous', False)
    username = request_data.get('username', None)
    about = request_data.get('about', None)
    name = request_data.get('name', None)
    try:
        email = request_data['email'].encode('utf-8')
    except Exception as e:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if add_user(username, email, name, is_anonymous, about) is False:
        result = user_table(email)
        about = result[0][5]
        email = result[0][2]
        user_id = result[0][0]
        is_anonymous = result[0][4]
        name = result[0][3]
        username = result[0][2]
    else:
        user_id = get_user_id_by_email(email)
    result = {'about': about,
              'email': email,
              'id': user_id,
              'isAnonymous': is_anonymous,
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
    request_data = json.loads(request.body)
    try:
        follower = request_data['follower'].encode('utf-8')
        followee = request_data['followee'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if follower == followee:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = subscribe(follower, followee)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_unfollow(request):
    request_data = json.loads(request.body)
    try:
        follower = request_data['follower'].encode('utf-8')
        followee = request_data['followee'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if follower == followee:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = unsubscribe(follower, followee)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_listFollowers(request):
    order = request.GET.get('order', 'desc')
    limit = request.GET.get('limit', '')
    since_id = request.GET.get('since_id', 0)
    try:
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
    limit = request.GET.get('limit', '')
    since_id = request.GET.get('since_id', 0)
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = list_following(limit, order, since_id, email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    answer = [user_info(row) for row in result]
    return HttpResponse(json.dumps(success(answer)), content_type='application/json')


def user_listPosts(request):
    since = request.GET.get('since', '')
    limit = request.GET.get('limit', '')
    order = request.GET.get('order', 'desc')
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    posts = post_created_by_user(email, since, limit, order)
    if posts is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [post_info(post, False, False, False) for post in posts]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_updateProfile(request):
    request_data = json.loads(request.body)

    about = request_data.get('about', None)
    name = request_data.get('name', None)

    try:
        email = request_data['user'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = update(name, about, email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def forum_create(request):
    request_data = json.loads(request.body)
    name = request_data.get('name', None).encode('utf-8')
    try:
        short_name = request_data['short_name'].encode('utf-8')
        email = request_data['user'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = get_user_id_by_email(email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if add_forum(name, short_name, user_id) is False:
        forum = forum_table(short_name)
        result = {'id': forum[0][0],
                  'name': forum[0][1],
                  'short_name': forum[0][2],
                  'user': get_user_email_by_id(forum[0][3])
        }
    else:
        forum_id = get_forum_id(short_name)
        result = {'id': forum_id,
                  'name': name,
                  'short_name': short_name,
                  'user': email
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
    limit = request.GET.get('limit', '')
    since_id = request.GET.get('since_id', 0)
    try:
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
    limit = request.GET.get('limit', '')
    since = request.GET.get('since', '')
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
    threads = list_thread(limit, order, since, short_name)
    if threads is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [thread_info(thread, short_name, include_forum, include_user) for thread in threads]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def forum_listPosts(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    limit = request.GET.get('limit', '')
    since = request.GET.get('since', '')
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
    posts = list_post(limit, order, since, short_name)
    if posts is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [post_info(post, include_user, include_forum, include_thread) for post in posts]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_create(request):
    request_data = json.loads(request.body)

    is_deleted = request_data.get('isDeleted', False)
    is_closed = request_data.get('isClosed', False)
    title = request_data.get('title', None).encode('utf-8')
    message = request_data.get('message', None).encode('utf-8')
    try:
        short_name = request_data['forum'].encode('utf-8')
        email = request_data['user'].encode('utf-8')
        date = request_data['date'].encode('utf-8')
        slug = request_data['slug'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = get_user_id_by_email(email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    forum_id = get_forum_id(short_name)
    if forum_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if add_thread(title, message, slug, is_closed, is_deleted, date, forum_id, user_id) is True:
        id = get_thread_id(slug)
        result = {'date': date,
                  'forum': short_name,
                  'id': id,
                  'isClosed': is_closed,
                  'isDeleted': is_deleted,
                  'message': message,
                  'slug': slug,
                  'title': title,
                  'user': email
        }
    else:
        thread = thread_info(id, short_name, False, False)
        result = {'date': thread['date'],
                  'forum': thread['forum'],
                  'id': thread['id'],
                  'isClosed': thread['isClosed'],
                  'isDeleted': thread['isDeleted'],
                  'message': thread['message'],
                  'slug': thread['slug'],
                  'title': thread['title'],
                  'user': thread['user']
        }
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_close(request):
    request_data = json.loads(request.body)

    try:
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if mark_flag_is_open_in_thread(thread_id, True) is None:
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
    since = request.GET.get('since', '')
    limit = request.GET.get('limit', '')

    if email == short_name and email is None:
        return HttpResponse(json.dumps(success(error())), content_type='application/json')
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
    since = request.GET.get('since', '')
    limit = request.GET.get('limit', '')
    try:
        thread = request.GET['thread']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    posts = list_thread_posts(thread, since, order, limit)
    if posts is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [post_info(post, False, False, False) for post in posts]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_open(request):
    request_data = json.loads(request.body)

    try:
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    thread_id = mark_flag_is_open_in_thread(thread_id, False)
    if thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_remove(request):
    request_data = json.loads(request.body)

    try:
        thread = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    thread_id = mark_flag_is_deleted_in_thread(thread, True)
    if thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_restore(request):
    request_data = json.loads(request.body)

    try:
        thread = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    thread_id = mark_flag_is_deleted_in_thread(thread, False)
    if thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_subscribe(request):
    request_data = json.loads(request.body)
    try:
        email = request_data['user']
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if subscribe_to_thread(thread_id, email) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id, 'user': email}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_unsubscribe(request):
    request_data = json.loads(request.body)

    try:
        email = request_data['user']
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if unsubscribe_to_thread(thread_id, email) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = {'thread': thread_id, 'user': email}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def thread_update(request):
    request_data = json.loads(request.body)
    try:
        message = request_data['message'].encode('utf-8')
        slug = request_data['slug'].encode('utf-8')
        thread_id = request_data['thread']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if update_thread(thread_id, message, slug) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(thread_info(thread_id, forum_thread(thread_id), False, False))),
                        content_type='application/json')


def thread_vote(request):
    request_data = json.loads(request.body)
    try:
        vote = request_data['vote']
        thread_id = request_data['thread']
    except Exception:
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
    request_data = json.loads(request.body)

    parent = request_data.get('parent', None)
    message = request_data.get('message', None)
    is_approved = request_data.get('isApproved', False)
    is_highlighted = request_data.get('isHighlighted', False)
    is_edited = request_data.get('isEdited', False)
    is_spam = request_data.get('isSpam', False)
    is_deleted = request_data.get('isDeleted', False)

    try:
        date = request_data['date'].encode('utf-8')
        thread_id = request_data['thread']

        email = request_data['user'].encode('utf-8')
        short_name = request_data['forum'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user_id = get_user_id_by_email(email)
    if user_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    slug = get_thread_slug(thread_id)
    if slug is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    post_id = add_post(message, is_approved, is_highlighted, is_edited,
                       is_spam, is_deleted, date, thread_id, user_id, parent)
    result = {'date': date,
              'forum': short_name,
              'id': post_id,
              'isApproved': is_approved,
              'isDeleted': is_deleted,
              'isEdited': is_edited,
              'isHighlighted': is_highlighted,
              'isSpam': is_spam,
              'message': message,
              'thread': thread_id,
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

    result = post_info(post_id, include_user, include_forum, include_thread)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def post_lists(request):
    since = request.GET.get('since', '')
    limit = request.GET.get('limit', '')
    order = request.GET.get('order', 'desc')

    short_name = request.GET.get('forum', None)
    thread_id = request.GET.get('thread', None)

    if short_name == thread_id and thread_id is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if thread_id is None:
        posts = list_post(limit, order, since, short_name)
    else:
        posts = list_thread_posts(thread_id, since, order, limit)
    if posts is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = [post_info(post, False, False, False) for post in posts]
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def post_remove(request):
    request_data = json.loads(request.body)
    try:
        post_id = request_data['post']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if mark_flag_is_deleted(post_id, True) is True:
        result = {'post': post_id}
        return HttpResponse(json.dumps(success(result)), content_type='application/json')
    else:
        return HttpResponse(json.dumps(error()), content_type='application/json')


def post_restore(request):
    request_data = json.loads(request.body)
    try:
        post_id = request_data['post']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if mark_flag_is_deleted(post_id, False) is True:
        result = {'post': post_id}
        return HttpResponse(json.dumps(success(result)), content_type='application/json')
    else:
        return HttpResponse(json.dumps(error()), content_type='application/json')


def post_update(request):
    request_data = json.loads(request.body)
    try:
        post_id = request_data['post']
        message = request_data['message']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    if update_post(post_id, message) is True:
        result = post_info(post_id, False, False, False)
        return HttpResponse(json.dumps(success(result)), content_type='application/json')
    else:
        return HttpResponse(json.dumps(error()), content_type='application/json')


def post_vote(request):

    request_data = json.loads(request.body)
    try:
        post_id = request_data['post']
        vote = request_data['vote']
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    like = 0
    dislike = 0
    if vote == 1:
        like = 1
    else:
        dislike = 1
    point = like - dislike
    if vote_post(post_id, like, dislike, point) is False:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = post_info(post_id, False, False, False)
    return HttpResponse(json.dumps(success(result)), content_type='application/json')





