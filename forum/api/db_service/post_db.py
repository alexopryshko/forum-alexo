from thread_db import *
__author__ = 'alexander'

db = get_connect()

def post_table(post_id):
    cursor = db.cursor()
    cursor.execute("""SELECT id, message, likes, dislikes, points,
                      isApproved, isHighlighted, isEdited, isSpam,
                      isDeleted, date, Threads_id, Users_id, parent
                      FROM Posts WHERE id = %s""", (post_id,))
    post = cursor.fetchall()
    if len(post) > 0:
        return post[0]
    else:
        return None

def post_info(post_id, short_name, include_user, include_forum, include_thread):
    post = post_table(post_id)
    if post is None:
        return None
    result = {'date':          post[10].strftime('%Y-%m-%d %H:%M:%S'),
              'dislikes':      post[3],
              'forum':         {},
              'id':            post[0],
              'isApproved':    post[5],
              'isDeleted':     post[9],
              'isEdited':      post[7],
              'isHighlighted': post[6],
              'isSpam':        post[8],
              'likes':         post[2],
              'message':       post[1],
              'parent':        post[13],
              'points':        post[4],
              'thread':        {},
              'user':          {},
    }
    if include_forum is True:
        result['forum'] = forum_info(short_name, False)
    else:
        result['forum'] = short_name

    email = get_user_email_by_id(post[12])
    if include_user is True:
        result['user'] = user_info(email)
    else:
        result['user'] = email

    if include_thread is True:
        result['thread'] = thread_info(post[11], short_name, False, False)
    else:
        result['thread'] = get_thread_slug(post[11])
    return result

def add_post(message,
             is_approved,
             is_highlighted,
             is_edited,
             is_spam,
             is_deleted,
             date,
             thread_id,
             user_id,
             parent):
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Posts (message, likes, dislikes, points, isApproved,
                          isHighlighted, isEdited, isSpam, isDeleted, date,
                          Threads_id, Users_id, parent)
                          VALUES (%s, 0, 0, 0, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                          (message, is_approved, is_highlighted, is_edited, is_spam,
                          is_deleted, date, thread_id, user_id, parent))
        post_id = cursor.execute("""SELECT id FROM Posts""")
        db.commit()
        cursor.close()
        return post_id
    except MySQLdb.Error:
        db.rollback()
        return 0


