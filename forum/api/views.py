from django.shortcuts import render
from django.http import HttpResponse
import json
import MySQLdb

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
              'username': resExec[0][2]}
    cursor.close()
    return result


def user_details(request):
    if request.method == "GET":
        email = request.GET['user']
        result = user_info(email)
        return HttpResponse(json.dumps(result), content_type='application/json')
    return HttpResponse(json.dumps(0), content_type='application/json')

def user_follow(request):
    follower = request.POST['follower']
    followee = request.POST['followee']
    #follower = "user1@yandex.ru"
    #followee = "alex@yandex.ru"

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
    follower = request.POST['follower']
    followee = request.POST['followee']
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
    #name = request.POST('name')
    #short_name = request.POST('short_name')
    #email = request.POST('user')

    name = 'LargeForumName8'
    short_name = 'ShortName8'
    email = 'user1@yandex.ru'

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









