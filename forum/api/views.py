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







