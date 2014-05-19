from helper import *
from django.db import connection
from django.db import IntegrityError
from api.db_service.thread_db import Thread
from api.db_service.user_db import User
from api.db_service.forum_db import Forum
__author__ = 'alexander'


class Post:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.message = kwargs.get("message")
        self.likes = kwargs.get("likes")
        self.dislikes = kwargs.get("dislikes")
        self.points = kwargs.get("points")
        self.is_approved = kwargs.get("is_approved")
        self.is_highlighted = kwargs.get("is_approved")
        self.is_edited = kwargs.get("is_edited")
        self.is_spam = kwargs.get("is_spam")
        self.is_deleted = kwargs.get("is_deleted")
        self.date = kwargs.get("date")
        self.thread = kwargs.get("thread")
        self.user = kwargs.get("user")
        self.forum = kwargs.get("forum")
        self.parent = kwargs.get("parent")

    def save(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Posts (
                                            message,
                                            likes,
                                            dislikes,
                                            points,
                                            isApproved,
                                            isHighlighted,
                                            isEdited,
                                            isSpam,
                                            isDeleted,
                                            date,
                                            Threads_id,
                                            Users_id,
                                            forum,
                                            parent
                              ) VALUES (%s, 0, 0, 0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                self.message,
                self.is_approved,
                self.is_highlighted,
                self.is_edited,
                self.is_spam,
                self.is_deleted,
                self.date,
                self.thread,
                self.user,
                self.forum,
                self.parent))
            self.id = cursor.execute("""SELECT id FROM Posts""")
            connection.commit()
        except IntegrityError:
            connection.rollback()
        cursor.close()

    def update(self):
        query = """UPDATE Posts SET """
        if self.is_deleted is not None:
            query += """isDeleted = {}, """.format(self.is_deleted)
        if self.message is not None:
            query += """message = '{}', """.format(self.message)
        if self.likes is not None:
            query += """likes = likes + {}, """.format(self.likes)
        if self.dislikes is not None:
            query += """dislikes = dislikes + {}, """.format(self.dislikes)
        if self.points is not None:
            query += """points = points +{}, """.format(self.points)
        query += """date = date WHERE id = %s"""
        cursor = connection.cursor()
        try:
            cursor.execute(query, (self.id,))
            connection.commit()
            cursor.close()
            return True
        except IntegrityError:
            connection.rollback()
            cursor.close()
            return False

    @staticmethod
    def get_inf(post_id, include_user=False, include_thread=False, include_forum=False):
        cursor = connection.cursor()
        cursor.execute("""SELECT id,
                                 message,
                                 likes,
                                 dislikes,
                                 points,
                                 isApproved,
                                 isHighlighted,
                                 isEdited,
                                 isSpam,
                                 isDeleted,
                                 date,
                                 Threads_id as thread,
                                 Users_id as user,
                                 parent,
                                 forum
                          FROM Posts WHERE id = %s""", (post_id,))
        result = dictfetch(cursor)
        if include_forum:
            result['forum'] = Forum.get_inf(short_name=result['forum'])
        if include_thread:
            #todo add thread inf
            result['thread'] = Thread.get_inf(result['thread'])
        result['user'] = User.get_inf(include_user, id=result['user'])
        result['date'] = result['date'].strftime('%Y-%m-%d %H:%M:%S')
        return result

    @staticmethod
    def list_posts(since, limit, order, **kwargs):
        forum = kwargs.get("forum")
        thread = kwargs.get("thread")
        query = """SELECT t1.id,
                          t1.message,
                          t1.likes,
                          t1.dislikes,
                          t1.points,
                          t1.isApproved,
                          t1.isHighlighted,
                          t1.isEdited,
                          t1.isSpam,
                          t1.isDeleted,
                          t1.date,
                          t1.Threads_id as thread,
                          t1.parent,
                          t1.forum,
                          t2.email as user
                         FROM Posts as t1
                         INNER JOIN Users as t2 ON t1.Users_id = t2.id """
        if forum is not None:
            query_param = forum
            query += """WHERE t1.forum = %s """
        elif thread is not None:
            query_param = thread
            query += """WHERE t1.Threads_id = %s """
        else:
            return None
        if since is not None:
            query += """AND t1.date > '{}' """.format(since)
        query += """ORDER BY t1.date """.format(order)
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor = connection.cursor()
        cursor.execute(query, (query_param,))
        result = dictfetchall(cursor)
        for item in result:
            item['date'] = item['date'].strftime('%Y-%m-%d %H:%M:%S')
        return result





# def post_table(post_id):
#
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id,
#                              message,
#                              likes,
#                              dislikes,
#                              points,
#                              isApproved,
#                              isHighlighted,
#                              isEdited,
#                              isSpam,
#                              isDeleted,
#                              date,
#                              Threads_id,
#                              Users_id,
#                              parent
#                       FROM Posts WHERE id = %s""", (post_id,))
#     post = cursor.fetchall()
#     cursor.close()
#
#     if len(post) > 0:
#         return post[0]
#     else:
#         return None
#
# def is_exist(post_id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT count(*) FROM Posts WHERE id = %s;""", (post_id,))
#     count = cursor.fetchall()
#     cursor.close()
#     return 1 == count[0][0]
#
#
# def post_info(post_id, include_user, include_forum, include_thread):
#     post = post_table(post_id)
#     if post is None:
#         return None
#     result = {'date':          post[10].strftime('%Y-%m-%d %H:%M:%S'),
#               'dislikes':      post[3],
#               'forum':         {},
#               'id':            post[0],
#               'isApproved':    post[5],
#               'isDeleted':     post[9],
#               'isEdited':      post[7],
#               'isHighlighted': post[6],
#               'isSpam':        post[8],
#               'likes':         post[2],
#               'message':       post[1],
#               'parent':        post[13],
#               'points':        post[4],
#               'thread':        {},
#               'user':          {},
#     }
#     short_name = forum_thread(post[11])
#     if include_forum is True:
#         result['forum'] = forum_info(short_name, False)
#     else:
#         result['forum'] = short_name
#
#     email = get_user_email_by_id(post[12])
#     if include_user is True:
#         result['user'] = user_info(email)
#     else:
#         result['user'] = email
#
#     if include_thread is True:
#         result['thread'] = thread_info(post[11], short_name, False, False)
#     else:
#         result['thread'] = post[11]
#     return result
#
# def add_post(message,
#              is_approved,
#              is_highlighted,
#              is_edited,
#              is_spam,
#              is_deleted,
#              date,
#              thread_id,
#              user_id,
#              parent):
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""INSERT INTO Posts (message, likes, dislikes, points, isApproved,
#                           isHighlighted, isEdited, isSpam, isDeleted, date,
#                           Threads_id, Users_id, parent)
#                           VALUES (%s, 0, 0, 0, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
#                           (message, is_approved, is_highlighted, is_edited, is_spam,
#                           is_deleted, date, thread_id, user_id, parent))
#         post_id = cursor.execute("""SELECT id FROM Posts""")
#         connection.commit()
#         cursor.close()
#         return post_id
#     except IntegrityError:
#         connection.rollback()
#         cursor.close()
#         return 0
#
# def mark_flag_is_deleted(post_id, flag):
#     if is_exist(post_id):
#         cursor = connection.cursor()
#         try:
#             cursor.execute("""UPDATE Posts SET isDeleted = {}, date = date WHERE id = %s""".format(flag), (post_id,))
#             connection.commit()
#             cursor.close()
#             return True
#         except IntegrityError:
#             connection.rollback()
#             cursor.close()
#             return False
#     else:
#         return False
#
# def update_post(post_id, message):
#     if is_exist(post_id):
#         cursor = connection.cursor()
#         try:
#             cursor.execute("""UPDATE Posts SET message = %s WHERE id = %s;""", (message, post_id))
#             connection.commit()
#             cursor.close()
#             return True
#         except IntegrityError:
#             connection.rollback()
#             cursor.close()
#             return False
#     else:
#         return False
#
# def vote_post(post_id, like, dislike, point):
#     if is_exist(post_id):
#         cursor = connection.cursor()
#         try:
#             cursor.execute("""UPDATE Posts SET likes = likes + %s,
#                                              dislikes = dislikes + %s,
#                                              points = points + %s,
#                                              date = date
#                                              WHERE id = %s;""", (like, dislike, point, post_id))
#             connection.commit()
#             cursor.close()
#             return True
#         except IntegrityError:
#             cursor.close()
#             connection.rollback()
#             return False
#     else:
#         return False
#
#
