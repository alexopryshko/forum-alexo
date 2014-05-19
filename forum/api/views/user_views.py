from django.http import HttpResponse
import json
from api.db_service.user_db import User
from api.db_service.helper import *
from django.utils.datastructures import MultiValueDictKeyError

__author__ = 'alexander'


def user_create(request):
    request_data = json.loads(request.body)
    #request_data = request.POST

    is_anonymous = request_data.get('isAnonymous', False)
    username = request_data.get('username', None)
    about = request_data.get('about', None)
    name = request_data.get('name', None)
    try:
        email = request_data['email'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')

    user = User(email=email, about=about, name=name, username=username, is_anonymous=is_anonymous)
    user.save()
    result = {'about': user.about,
              'email': user.email,
              'id': user.id,
              'isAnonymous': user.is_anonymous,
              'name': user.name,
              'username': user.username}
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_details(request):
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    #result = user_info(email)
    result = User.get_inf(details=True, email=email)
    if result is None:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_follow(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        follower = request_data['follower'].encode('utf-8')
        followee = request_data['followee'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if follower == followee:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = User.follow(follower, followee)
    if not result:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_unfollow(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    try:
        follower = request_data['follower'].encode('utf-8')
        followee = request_data['followee'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    if follower == followee:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = User.unfollow(follower, followee)
    if not result:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_listFollowers(request):
    order = request.GET.get('order', 'desc')
    limit = request.GET.get('limit')
    since_id = request.GET.get('since_id')
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = User.list_followers(limit, order, since_id, email)
    #if not result:
    #    return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_listFollowing(request):
    order = request.GET.get('order', 'desc')
    limit = request.GET.get('limit')
    since_id = request.GET.get('since_id')
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = User.list_following(limit, order, since_id, email)
    #if not result:
    #    return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_listPosts(request):
    since = request.GET.get('since')
    limit = request.GET.get('limit')
    order = request.GET.get('order', 'desc')
    try:
        email = request.GET['user']
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = User.list_posts(email, since, limit, order)
    #if not posts:
    #    return HttpResponse(json.dumps(error()), content_type='application/json')
    return HttpResponse(json.dumps(success(result)), content_type='application/json')


def user_updateProfile(request):
    request_data = json.loads(request.body)
    #request_data = request.POST
    about = request_data.get('about', None)
    name = request_data.get('name', None)
    try:
        email = request_data['user'].encode('utf-8')
    except Exception:
        return HttpResponse(json.dumps(error()), content_type='application/json')
    user = User(about=about, name=name, email=email)
    if not user.update():
        return HttpResponse(json.dumps(error()), content_type='application/json')
    result = User.get_inf(True, email=user.email)
    return HttpResponse(json.dumps(success(result)), content_type='application/json')