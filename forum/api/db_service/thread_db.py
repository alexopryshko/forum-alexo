from forum_db import *

__author__ = 'alexander'

db = get_connect()

def thread_table(id):
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Threads WHERE id = %s;""", (id,))
    thread = cursor.fetchall()
    cursor.close()
    if len(thread) > 0:
        return thread
    else:
        return None

def forum_thread(thread_id):
    cursor = db.cursor()
    cursor.execute("""SELECT Forums_id FROM Threads WHERE id = %s;""", (thread_id,))
    forum_id = cursor.fetchall()
    if len(forum_id) > 0:
        return get_short_name(forum_id[0][0])
    else:
        return None

def get_thread_slug(id):
    cursor = db.cursor()
    cursor.execute("""SELECT slug FROM Threads WHERE id = %s;""", (id,))
    thread = cursor.fetchall()
    cursor.close()
    if len(thread) > 0:
        return thread[0][0]
    else:
        return None

def get_thread_id(slug):
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM Threads WHERE slug = %s""", (slug,))
    thread = cursor.fetchall()
    cursor.close()
    if len(thread) > 0:
        return thread[0][0]
    else:
        return None

def number_of_posts(thread_id):
    cursor = db.cursor()
    cursor.execute("""SELECT count(*) AS t FROM Posts WHERE Threads_id = {}""".format(thread_id))
    result = cursor.fetchall()
    return result[0][0]

def thread_info(id, short_name, include_forum, include_user):
    thread = thread_table(id)
    if thread is None:
        return None
    result = {'date':           thread[0][9].strftime('%Y-%m-%d %H:%M:%S'),
              'dislikes':       thread[0][5],
              'forum':          {},
              'id':             thread[0][0],
              'isClosed':       thread[0][7],
              'isDeleted':      thread[0][8],
              'likes':          thread[0][4],
              'message':        thread[0][2],
              'points':         thread[0][6],
              'posts':          number_of_posts(thread[0][0]),
              'slug':           thread[0][3],
              'title':          thread[0][1],
              'user':           {}
    }

    email = get_user_email_by_id(thread[0][11])
    if include_user is True:
        result['user'] = user_info(email)
    else:
        result['user'] = email
    if include_forum is True:
        result['forum'] = forum_info(short_name, False)
    else:
        result['forum'] = short_name
    return result

def add_thread(title, message, slug, is_closed, is_deleted, date, forum_id, user_id):
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Threads (title, message, slug, likes,
                          dislikes, points, isClosed, isDeleted,
                          date, Forums_id, Users_id)
                          VALUES(%s, %s, %s, 0, 0, 0, %s, %s, %s, %s, %s)""",
                          (title, message, slug, is_closed, is_deleted, date, forum_id, user_id))
        db.commit()
        cursor.close()
        return True
    except MySQLdb.Error:
        db.rollback()
        cursor.close()
        return False

def mark_as_closed(thread_id):
    cursor = db.cursor()
    if get_thread_slug(thread_id) is None:
        return None
    try:
        cursor.execute("""UPDATE Threads SET isClosed = TRUE WHERE id = %s""", (thread_id,))
        db.commit()
        result = thread_id
    except MySQLdb.Error:
        db.rollback()
    cursor.close()
    return result

def mark_as_open(thread_id):
    cursor = db.cursor()
    if get_thread_slug(thread_id) is None:
        return None
    try:
        cursor.execute("""UPDATE Threads SET isClosed = FALSE WHERE id = %s""", (thread_id,))
        db.commit()
        result = thread_id
    except MySQLdb.Error:
        db.rollback()
    cursor.close()
    return result

def list_thread_posts(thread_id, since, order, limit):
    slug = get_thread_slug(thread_id)
    if slug is None:
        return None
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM Posts
                      WHERE Threads_id = %s and date > {}
                      ORDER BY date {}
                      LIMIT {}""".format(since, order, limit), (thread_id,))
    posts = cursor.fetchall()
    return posts

def mark_as_deleted(thread_id):
    cursor = db.cursor()
    if get_thread_slug(thread_id) is None:
        return None
    try:
        cursor.execute("""UPDATE Threads SET isDeleted = TRUE WHERE id = %s""", (thread_id,))
        db.commit()
        result = thread_id
    except MySQLdb.Error:
        db.rollback()
    cursor.close()
    return result

def mark_as_restored(thread_id):
    cursor = db.cursor()
    if get_thread_slug(thread_id) is None:
        return None
    try:
        cursor.execute("""UPDATE Threads SET isDeleted = FALSE WHERE id = %s""", (thread_id,))
        db.commit()
        result = thread_id
    except MySQLdb.Error:
        db.rollback()
    cursor.close()
    return result

def subscribe_to_thread(thread_id, email):
    user_id = get_user_id_by_email(email)
    if user_id is None:
        return False
    slug = get_thread_slug(thread_id)
    if slug is None:
        return False
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Users_has_Threads (Users_id, Threads_id) VALUES(%s,%s);""", (user_id, thread_id,))
        db.commit()
        result = True
    except MySQLdb.Error:
        db.rollback()
        result = False
    cursor.close()
    return result

def unsubscribe_to_thread(thread_id, email):
    user_id = get_user_id_by_email(email)
    if user_id is None:
        return False
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Users_has_Threads WHERE Users_id = %s AND Threads_id = %s;""", (user_id, thread_id,))
    answer = cursor.fetchall()
    if len(answer) == 0:
        return False
    try:
        cursor.execute("""DELETE FROM Users_has_Threads WHERE Users_id = %s AND Threads_id = %s;""", (user_id, thread_id,))
        db.commit()
        result = True
    except MySQLdb.Error:
        db.rollback()
        result = False
    cursor.close()
    return result

def update_thread(thread_id, message, slug):
    test = get_thread_slug(thread_id)
    if test is None:
        return False
    cursor = db.cursor()
    try:
        cursor.execute("""UPDATE Threads SET message = %s, slug = %s WHERE id = %s;""", (message, slug, thread_id,))
        db.commit()
        result = True
    except MySQLdb.Error:
        db.rollback()
        result = False
    cursor.close()
    return result

def vote_thread(thread_id, like, dislike, points):
    slug = get_thread_slug(thread_id)
    if slug is None:
        return False
    cursor = db.cursor()
    try:
        cursor.execute("""UPDATE Threads SET likes = likes + %s,
                                             dislikes = dislikes + %s,
                                             points = points + %s
                                             WHERE id = %s;""", (like, dislike, points,thread_id,))
        db.commit()
        result = True
    except MySQLdb.Error:
        db.rollback()
        result = False
    cursor.close()
    return result






