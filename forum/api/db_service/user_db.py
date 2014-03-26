from connect import get_connect
import MySQLdb

__author__ = 'alexander'

db = get_connect()

def get_user_email_by_id(user_id):
    cursor = db.cursor()
    cursor.execute("""SELECT email FROM Users WHERE id = %s; """, (user_id,))
    email = cursor.fetchall()
    cursor.close()
    if len(email) > 0:
        return email[0][0]
    else:
        return None

def get_user_id_by_email(email):
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
    id = cursor.fetchall()
    cursor.close()
    if len(id) > 0:
        return id[0][0]
    else:
        return None

def user_table(email):
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Users WHERE email = %s; """, (email,))
    result = cursor.fetchall()
    cursor.close()
    if len(result) > 0:
        return result
    else:
        return None

def user_info(email):
    result = user_table(email)
    if result is None:
        return None

    cursor = db.cursor()
    cursor.execute("""SELECT t2.email FROM Users AS t1
                          INNER JOIN Users_has_Users AS t ON t.Users_id = t1.id
                          INNER JOIN Users AS t2 ON t.Users_id1 = t2.id
                          WHERE t1.email = %s AND t1.id != t2.id""", (email,))
    followers = cursor.fetchall()
    if len(followers) > 0:
        followers = followers[0]

    count = cursor.execute("""SELECT t2.email FROM Users AS t1
                                  INNER JOIN Users_has_Users AS t ON t.Users_id1 = t1.id
                                  INNER JOIN Users AS t2 ON t.Users_id = t2.id
                                  WHERE t1.email = %s AND t1.id != t2.id""", (email,))
    following = cursor.fetchall()
    if len(following) > 0:
        following = following[0]

    result = {'about': result[0][5],
              'email': result[0][2],
              'followers': followers,
              'following': following,
              'id': result[0][0],
              'isAnonymous': result[0][4],
              'name': result[0][3],
              'subscriptions': count,
              'username': result[0][1]}
    cursor.close()
    return result

def informationAboutUser(user_id, flag):
    email = get_user_email_by_id(user_id)
    if flag:
        return user_info(email)
    else:
        return email

def add_user(username, email, name, isAnonymous, about):
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Users (username, email, name, isAnonymous, about)
                          VALUES (%s, %s, %s, %s, %s);""", (username, email, name, isAnonymous, about))
        db.commit()
        cursor.close()
        return True
    except MySQLdb.Error:
        db.rollback()
        cursor.close()
        return False

def subscribe(follower, followee):

    follower_id = get_user_id_by_email(follower)
    if follower_id is None:
        return None

    followee_id = get_user_id_by_email(followee)
    if followee_id is None:
        return None

    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Users_has_Users (Users_id, Users_id1)
                             VALUES (%s, %s);""", (followee_id, follower_id))
        db.commit()
    except MySQLdb.Error:
        db.rollback()

    cursor.close()
    return user_info(follower)

def unsubscribe(follower, followee):
    follower_id = get_user_id_by_email(follower)
    if follower_id is None:
        return None

    followee_id = get_user_id_by_email(followee)
    if followee_id is None:
        return None
    cursor = db.cursor()
    try:
        cursor.execute("""DELETE FROM Users_has_Users WHERE
                          users_id = %s AND users_id1 = %s""", (followee_id, follower_id))
        db.commit()
    except MySQLdb.Error:
        db.rollback()

    cursor.close()
    return user_info(follower)

def list_followers(limit, order, since_id, email):
    cursor = db.cursor()

    id = get_user_id_by_email(email)
    if id is None:
        return None

    cursor.execute("""SELECT t2.email FROM Users AS t1
                          INNER JOIN Users_has_Users AS t ON t.Users_id = t1.id
                          INNER JOIN Users AS t2 ON t.Users_id1 = t2.id
                          WHERE t1.id = %s AND t1.id != t2.id AND t2.id >= {}
                          ORDER BY t2.name {}
                          LIMIT {}""".format(since_id, order, limit), (id, ))
    followers = cursor.fetchall()
    cursor.close()
    return followers

def list_following(limit, order, since_id, email):
    cursor = db.cursor()

    id = get_user_id_by_email(email)
    if id is None:
        return None

    cursor = db.cursor()
    cursor.execute("""SELECT t2.email FROM Users AS t1
                          INNER JOIN Users_has_Users AS t ON t.Users_id1 = t1.id
                          INNER JOIN Users AS t2 ON t.Users_id = t2.id
                          WHERE t1.id = %s AND t1.id != t2.id AND t2.id >= {}
                          ORDER BY t2.name {}
                          LIMIT {}""".format(since_id, order, limit), (id, ))
    following = cursor.fetchall()
    cursor.close()
    return following

def update(name, about, email):
    cursor = db.cursor()
    result = None
    try:
        cursor.execute("""UPDATE Users SET name= %s, about = %s WHERE email= %s""", (name, about, email))
        db.commit()
        result = user_info(email)
    except MySQLdb.Error:
        db.rollback()
    cursor.close()
    return result