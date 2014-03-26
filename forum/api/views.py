from django.http import HttpResponse
import json
from db_service.forum_db import *
from django.utils.datastructures import MultiValueDictKeyError

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

def getUserEmailByID(user_id):
    cursor = db.cursor()
    cursor.execute("""SELECT email FROM Users WHERE id = %s; """, (user_id,))
    email = cursor.fetchall()
    print email
    cursor.close()
    return email

def getForumInfByID(forum_id, flag):
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Forums WHERE id = %s;""", (forum_id,))
    forum = cursor.fetchall()

    if flag:
        result = {'id': forum[0][0],
                  'name': forum[0][1],
                  'short_name': forum[0][2],
                  'user': getUserEmailByID(forum[0][3])}
    else:
        result = forum[0][2]
    cursor.close()
    return result

def countPosts(thread_id):
    cursor = db.cursor()
    cursor.execute("""SELECT count(*) AS t FROM Posts WHERE Threads_id = {}""".format(thread_id))
    result = cursor.fetchall()
    return result[0][0]

def getThreadByID(thread_id, include_user, include_forum, details):
    if details == False:
        return thread_id
    cursor = db.cursor()

    cursor.execute("""SELECT * FROM Threads WHERE id = %s;""", (thread_id,))
    thread = cursor.fetchall()

    if thread:
        result = {'date': thread[0][9].strftime('%Y-%m-%d %H:%M:%S'),
                   'dislikes': thread[0][5],
                   'forum': getForumInfByID(thread[0][10], include_forum),
                   'id': thread[0][0],
                   'isClosed': thread[0][7],
                   'isDeleted': thread[0][8],
                   'likes': thread[0][4],
                   'message': thread[0][2],
                   'points': thread[0][6],
                   'posts': countPosts(thread[0][0]),
                   'slug': thread[0][3],
                   'title': thread[0][1],
                   'user': informationAboutUser(thread[0][11], include_user)}
        return result
    else:
        return {}



def forum_listThreads(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        result = {}
        return HttpResponse(json.dumps(result), content_type='application/json')

    includeUser = False
    includeForum = False
    if 'user' in related:
        includeUser = True
    if 'forum' in related:
        includeForum = True

    cursor = db.cursor()

    cursor.execute("""SELECT t2.id, t2.title, t2.message, t2.slug, t2.likes, t2.dislikes,
                             t2.points, t2.isClosed, t2.isDeleted, t2.date, t2.Forums_id, t2.Users_id FROM Threads AS t2
                      INNER JOIN Forums AS t1 ON t1.id = t2.Forums_id
                      WHERE t1.short_name = %s AND t2.id > {}
                      ORDER BY t2.date {}
                      LIMIT {}""".format(since_id, order, limit), (short_name,))
    threads = cursor.fetchall()

    result = [{'date': thread[9].strftime('%Y-%m-%d %H:%M:%S'),
               'dislikes': thread[5],
               'forum': getForumInfByID(thread[10], includeForum),
               'id': thread[0],
               'isClosed': thread[7],
               'isDeleted': thread[8],
               'likes': thread[4],
               'message': thread[2],
               'points': thread[6],
               'posts': countPosts(thread[0]),
               'slug': thread[3],
               'title': thread[1],
               'user': informationAboutUser(thread[11], includeUser)} for thread in threads]
    return HttpResponse(json.dumps(result), content_type='application/json')

def forum_listPosts(request):
    order = request.GET.get('order', 'desc')
    related = request.GET.get('related', '[]')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        result = {}
        return HttpResponse(json.dumps(result), content_type='application/json')

    include_user = False
    include_forum = False
    include_thread = False
    if 'user' in related:
        include_user = True
    if 'forum' in related:
        include_forum = True
    if 'thread' in related:
        include_thread = True

    cursor = db.cursor()

    cursor.execute("""SELECT t3.id, t3.message, t3.likes, t3.dislikes,
                             t3.points, t3.isApproved, t3.isHighlighted, t3.isEdited,
                             t3.isSpam, t3.isDeleted, t3.date, t3.Threads_id,
                             t3.Users_id, t3.parent, t1.id FROM Threads AS t2
                      INNER JOIN Forums AS t1 ON t1.id = t2.Forums_id
                      INNER JOIN Posts AS t3 ON t2.id = t3.Threads_id
                      WHERE t1.short_name = %s AND t2.id > {}
                      ORDER BY t2.date {}
                      LIMIT {}""".format(since_id, order, limit), (short_name,))
    posts = cursor.fetchall()

    result = [{'date': post[10].strftime('%Y-%m-%d %H:%M:%S'),
               'dislikes': post[3],
               'forum': getForumInfByID(post[14], include_forum),
               'id': post[0],
               'isApproved': post[5],
               'isDeleted': post[9],
               'isEdited': post[7],
               'isHighlighted': post[6],
               'isSpam': post[8],
               'likes': post[2],
               'message': post[1],
               'parent': post[13],
               'points': post[4],
               'thread': getThreadByID(post[11], False, False, include_thread),
               'user': informationAboutUser(post[12], include_user)} for post in posts]

    return HttpResponse(json.dumps(result), content_type='application/json')





def thread_create(request):
    isDeleted = request.POST['isDeleted']
    short_name = request.POST['forum']
    title = request.POST['title']
    isClosed = request.POST['isClosed']
    email = request.POST['user']
    date = request.POST['date']
    message = request.POST['message']
    slug = request.POST['slug']



    #isDeleted = 0
    #short_name = 'ShortName1'
    #title = 'title1'
    #isClosed = 1
    #email = 'user1@mail.ru'
    #date = '2014-01-01 00:00:01'
    #message = 'message1'
    #slug = 'slug6'

    cursor = db.cursor()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
    user_id = cursor.fetchall()

    cursor.execute("""SELECT id FROM Forums WHERE short_name = %s;""", (short_name,))
    forum_id = cursor.fetchall()

    try:
        cursor.execute("""INSERT INTO Threads (title, message, slug, likes,
                          dislikes, points, isClosed, isDeleted,
                          date, Forums_id, Users_id)
                          VALUES(%s, %s, %s, 0, 0, 0, %s, %s, %s, %s, %s)""",
                          (title, message, slug, isClosed, isDeleted, date, forum_id, user_id))
        db.commit()

        cursor.execute("""SELECT id FROM Threads WHERE slug = %s""", (slug,))
        thread_id = cursor.fetchall()

        result = {'date': date,
              'forum': short_name,
              'id': thread_id[0][0],
              'isClosed': isClosed,
              'isDeleted': isDeleted,
              'message': message,
              'slug': slug,
              'title': title,
              'user': email}
    except MySQLdb.Error:
        db.rollback()
        result = {}

    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')



def post_create(request):
    if 'parent' in request.POST:
        parent = request.POST['parent']
    else:
        parent = None

    if 'isApproved' in request.POST:
        isApproved = request.POST['isApproved']
    else:
        isApproved = 0;

    if 'isHighlighted' in request.POST:
        isHighlighted = request.POST['isHighlighted']
    else:
        isHighlighted = 0;

    if 'isEdited' in request.POST:
        isEdited = request.POST['isEdited']
    else:
        isEdited = 0;

    if 'isSpam' in request.POST:
        isSpam = request.POST['isSpam']
    else:
        isSpam = 0;

    if 'isDeleted' in request.POST:
        isDeleted = request.POST['isDeleted']
    else:
        isDeleted = 0;

    date = request.POST['date']
    thread_id = request.POST['thread']
    message = request.POST['message']
    email = request.POST['user']
    short_name = request.POST['forum']

    #date = '2014-02-01 22:00:01'
    #thread_id = 5
    #message = 'message7'
    #email = 'user4@mail.ru'
    #short_name = 'ShortName4'

    cursor = db.cursor()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
    user_id = cursor.fetchall()

    try:
        cursor.execute("""INSERT INTO Posts (message, likes, dislikes, points, isApproved,
                          isHighlighted, isEdited, isSpam, isDeleted, date,
                          Threads_id, Users_id, parent)
                          VALUES (%s, 0, 0, 0, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                          (message, isApproved, isHighlighted, isEdited, isSpam,
                          isDeleted, date, thread_id, user_id, parent))
        post_id = cursor.execute("""SELECT id FROM Posts""")
        db.commit()

        result = {'date': date,
                  'forum': short_name,
                  'id': post_id,
                  'isApproved': isApproved,
                  'isDeleted': isDeleted,
                  'isEdited': isEdited,
                  'isHighlighted': isHighlighted,
                  'isSpam': isSpam,
                  'message': message,
                  'thread': thread_id,
                  'user': email}

    except MySQLdb.Error:
        db.rollback()
        result = {}

    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')






