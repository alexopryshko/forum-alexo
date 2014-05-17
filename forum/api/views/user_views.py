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

    is_anonymous = request_data.get('isAnonymous', False).encode('utf-8')
    username = request_data.get('username', None).encode('utf-8')
    about = request_data.get('about', None).encode('utf-8')
    name = request_data.get('name', None).encode('utf-8')
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
    #result = user_info(email)
    result = User.get(details=True, email=email)
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