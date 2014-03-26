from django.shortcuts import render
from django.http import HttpResponse
import json
import MySQLdb
from django.utils.datastructures import MultiValueDictKeyError

db = MySQLdb.connect(host="localhost", user="AlexO", passwd="pwd", db="tp_project_forum")

def user_create(request):
    if request.method == "POST":
        username = request.POST['username']
        about = request.POST['about']
        isAnonymous = request.POST['isAnonymous']
        name = request.POST['name']
        email = request.POST['email']
        cursor = db.cursor()
        try:
            cursor.execute("""INSERT INTO Users (username, email, name, isAnonymous, about)
                             VALUES (%s, %s, %s, %s, %s);""", (username, email, name, isAnonymous, about))
        except MySQLdb.Error, e:
            print "User exist"

        db.commit()

        cursor.execute("""SELECT * FROM Users WHERE email = %s; """, (email,))
        resExec = cursor.fetchall()
        result = {'about': resExec[0][5],
                  'email': resExec[0][2],
                  'id': resExec[0][0],
                  'isAnonymous': resExec[0][4],
                  'name': resExec[0][3],
                  'username': resExec[0][2]}
        cursor.close()
        return HttpResponse(json.dumps(result), content_type='application/json')
    return HttpResponse(json.dumps(0), content_type='application/json')


def user_info(email):
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Users WHERE email = %s; """, (email,))
    resExec = cursor.fetchall()

    cursor.execute("""SELECT t2.email FROM Users AS t1
                          INNER JOIN Users_has_Users AS t ON t.Users_id = t1.id
                          INNER JOIN Users AS t2 ON t.Users_id1 = t2.id
                          WHERE t1.email = %s AND t1.id != t2.id""", (email,))
    followers = cursor.fetchall()

    count = cursor.execute("""SELECT t2.email FROM Users AS t1
                                  INNER JOIN Users_has_Users AS t ON t.Users_id1 = t1.id
                                  INNER JOIN Users AS t2 ON t.Users_id = t2.id
                                  WHERE t1.email = %s AND t1.id != t2.id""", (email,))
    following = cursor.fetchall()

    result = {'about': resExec[0][5],
              'email': resExec[0][2],
              'followers': followers,
              'following': following,
              'id': resExec[0][0],
              'isAnonymous': resExec[0][4],
              'name': resExec[0][3],
              'subscriptions': count,
              'username': resExec[0][1]}
    cursor.close()
    return result

def informationAboutUser(user_id, flag):
    email = getUserEmailByID(user_id)
    if flag:
        return user_info(email)
    else:
        return email


def user_details(request):
    if request.method == "GET":
        email = request.GET['user']
        result = user_info(email)
        return HttpResponse(json.dumps(result), content_type='application/json')
    return HttpResponse(json.dumps(0), content_type='application/json')

def user_follow(request):
    #follower = request.POST['follower']
    #followee = request.POST['followee']
    follower = "user2@mail.ru"
    followee = "user1@mail.ru"

    cursor = db.cursor()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (follower,))
    follower_id = cursor.fetchall()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (followee,))
    followee_id = cursor.fetchall()

    try:
        cursor.execute("""INSERT INTO Users_has_Users (Users_id, Users_id1)
                             VALUES (%s, %s);""", (followee_id, follower_id))
    except MySQLdb.Error, e:
        print "User exist"

    db.commit()
    result = user_info(follower)
    return HttpResponse(json.dumps(result), content_type='application/json')

def user_listFollowers(request):
    limit = request.GET['limit']
    order = request.GET['order']
    since_id = request.GET['since_id']
    email = request.GET['user']
    if order is None:
        order = "desc"
    cursor = db.cursor()
    cursor.execute("""SELECT t2.email FROM Users AS t1
                          INNER JOIN Users_has_Users AS t ON t.Users_id = t1.id
                          INNER JOIN Users AS t2 ON t.Users_id1 = t2.id
                          WHERE t1.email = %s AND t1.id != t2.id AND t2.id >= {}
                          ORDER BY t2.name {}
                          LIMIT {}""".format(since_id, order, limit), (email, ))
    followers = cursor.fetchall()
    result = [user_info(row) for row in followers]
    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')

def user_listFollowing(request):
    limit = request.GET['limit']
    order = request.GET['order']
    since_id = request.GET['since_id']
    email = request.GET['user']

    if order is None:
        order = "desc"

    cursor = db.cursor()
    cursor.execute("""SELECT t2.email FROM Users AS t1
                          INNER JOIN Users_has_Users AS t ON t.Users_id1 = t1.id
                          INNER JOIN Users AS t2 ON t.Users_id = t2.id
                          WHERE t1.email = %s AND t1.id != t2.id AND t2.id >= {}
                          ORDER BY t2.name {}
                          LIMIT {}""".format(since_id, order, limit), (email, ))

    followers = cursor.fetchall()
    result = [user_info(row) for row in followers]
    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')

def user_unfollow(request):
    follower = "user2@mail.ru"
    followee = "user1@mail.ru"
    #follower = request.POST['follower']
    #followee = request.POST['followee']
    #followee = "email"
    #follower = "alex@yandex.ru"

    cursor = db.cursor()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (follower,))
    follower_id = cursor.fetchall()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (followee,))
    followee_id = cursor.fetchall()

    try:
        cursor.execute("""delete from Users_has_Users where
                          users_id = %s and users_id1 = %s""", (followee_id, follower_id))
        db.commit()
    except MySQLdb.Error, e:
        db.rollback()
        print "No follower"

    result = user_info(follower)

    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')

def user_updateProfile(request):
    about = request.POST['about']
    email = request.POST['user']
    name = request.POST['name']

    #about = 'test update'
    #email = 'user@mail.ru'
    #name = 'user'

    cursor = db.cursor()
    try:
        cursor.execute("""UPDATE Users SET name= %s, about = %s WHERE email= %s""", (name, about, email))
        db.commit()
    except MySQLdb.Error:
        db.rollback()
        print "User not exist"

    result = user_info(email)
    cursor.close()

    return HttpResponse(json.dumps(result), content_type='application/json')


def forum_create(request):
    name = request.POST['name']
    short_name = request.POST['short_name']
    email = request.POST['user']

    #name = 'LargeForumName8'
    #short_name = 'ShortName8'
    #email = 'user1@yandex.ru'

    cursor = db.cursor()

    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
    user_id = cursor.fetchall()

    try:
        cursor.execute("""INSERT INTO Forums (name, short_name, Users_id)
                          VALUE (%s, %s, %s);""", (name, short_name, user_id))
        db.commit()

        cursor.execute("""SELECT id FROM Forums WHERE short_name = %s;""", (short_name,))
        forum_id = cursor.fetchall()

        result = {'id': forum_id,
              'name': name,
              'short_name': short_name,
              'user': email}

    except MySQLdb.Error:
        db.rollback()
        print "User not exist"
        result = {}

    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')

def forum_details(request):
    related = request.GET['related']
    short_name = request.GET['forum']

    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Forums WHERE short_name = %s;""", (short_name,))
    forum = cursor.fetchall()

    user_id = forum[0][3]

    cursor.execute("""SELECT email FROM Users WHERE id = %s; """, (user_id,))
    email = cursor.fetchall()

    if related == "['users']":
        result = {'id': forum[0][0],
              'name': forum[0][1],
              'short_name': forum[0][2],
              'user': user_info(email)}
    else:
        result = {'id': forum[0][0],
                  'name': forum[0][1],
                  'short_name': forum[0][2],
                  'user': email}


    cursor.close()
    return HttpResponse(json.dumps(result), content_type='application/json')

def forum_listUsers(request):
    order = request.GET.get('order', 'desc')
    try:
        limit = request.GET['limit']
        since_id = request.GET['since_id']
        short_name = request.GET['forum']
    except MultiValueDictKeyError:
        result = {}
        return HttpResponse(json.dumps(result), content_type='application/json')

    cursor = db.cursor()
    cursor.execute("""SELECT DISTINCT t4.email FROM Forums AS t1
                      INNER JOIN Threads AS t2 ON t1.id = t2.Forums_id
                      INNER JOIN Posts AS t3 ON t2.id = t3.Threads_id
                      INNER JOIN Users AS t4 ON t3.Users_id = t4.id
                      WHERE t1.short_name = %s AND t4.id > {}
                      ORDER BY t3.date {}
                      LIMIT {}""".format(since_id, order, limit), (short_name,))
    users = cursor.fetchall()

    result = [user_info(user) for user in users]
    cursor.close()

    return HttpResponse(json.dumps(result), content_type='application/json')

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






