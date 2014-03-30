from user_db import *
import MySQLdb

__author__ = 'alexander'

db = get_connect()

def get_short_name(id):
    cursor = db.cursor()
    cursor.execute("""SELECT short_name FROM Forums WHERE id = %s;""", (id,))
    forum = cursor.fetchall()
    cursor.close()
    if len(forum) > 0:
        return forum[0][0]
    else:
        return None


def get_forum_id(short_name):
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM Forums WHERE short_name = %s;""", (short_name,))
    forum_id = cursor.fetchall()
    cursor.close()
    if len(forum_id) > 0:
        return forum_id[0][0]
    else:
        return None

def add_forum(name, short_name, user_id):
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Forums (name, short_name, Users_id)
                          VALUE (%s, %s, %s);""", (name, short_name, user_id))
        db.commit()
        cursor.close()
        return True
    except MySQLdb.Error:
        db.rollback()
        cursor.close()
        return False

def forum_table(short_name):
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM Forums WHERE short_name = %s;""", (short_name,))
    forum = cursor.fetchall()
    cursor.close()
    if len(forum) > 0:
        return forum
    else:
        return None

def forum_info(short_name, deployed):
    forum = forum_table(short_name)
    if forum is None:
        return None
    email = get_user_email_by_id(forum[0][3])
    result = {'id':         forum[0][0],
              'name':       forum[0][1],
              'short_name': forum[0][2],
              'user':       {}
    }

    if deployed is True:
        result['user'] = user_info(email)
    else:
        result['user'] = email
    return result

def list_users(limit, order, since_id, short_name):
    limit = limit_node(limit)

    forum_id = get_forum_id(short_name)
    if forum_id is None:
        return None
    cursor = db.cursor()
    cursor.execute("""SELECT DISTINCT t4.email FROM Forums AS t1
                      INNER JOIN Threads AS t2 ON t1.id = t2.Forums_id
                      INNER JOIN Posts AS t3 ON t2.id = t3.Threads_id
                      INNER JOIN Users AS t4 ON t3.Users_id = t4.id
                      WHERE t1.id = %s AND t4.id > {}
                      ORDER BY t3.date {}
                      {}""".format(since_id, order, limit), (forum_id,))
    result = cursor.fetchall()
    cursor.close()
    return result

def list_thread(limit, order, since, short_name):
    limit = limit_node(limit)
    since = since_node('t2.date', since)
    forum_id = get_forum_id(short_name)
    if forum_id is None:
        return None
    cursor = db.cursor()
    cursor.execute("""SELECT t2.id FROM Threads AS t2
                      INNER JOIN Forums AS t1 ON t1.id = t2.Forums_id
                      WHERE t1.id = %s {}
                      ORDER BY t2.date {}
                      {}""".format(since, order, limit), (forum_id,))
    threads = cursor.fetchall()
    cursor.close()
    return threads

def list_post(limit, order, since, short_name):
    limit = limit_node(limit)
    since = since_node('t3.date', since)
    forum_id = get_forum_id(short_name)
    if forum_id is None:
        return None
    cursor = db.cursor()
    cursor.execute("""SELECT t3.id FROM Threads AS t2
                      INNER JOIN Forums AS t1 ON t1.id = t2.Forums_id
                      INNER JOIN Posts AS t3 ON t2.id = t3.Threads_id
                      WHERE t1.id = %s {}
                      ORDER BY t3.date {}
                      {}""".format(since, order, limit), (forum_id,))
    posts = cursor.fetchall()
    cursor.close()
    return posts

