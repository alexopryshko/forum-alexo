from helper import *
from django.db import connection
from django.db import IntegrityError
from api.db_service.user_db import User
from api.db_service.forum_db import Forum


__author__ = 'alexander'


class Thread:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.message = kwargs.get("message")
        self.slug = kwargs.get("slug")
        self.likes = kwargs.get("likes")
        self.dislikes = kwargs.get("dislikes")
        self.points = kwargs.get("points")
        self.is_closed = kwargs.get("is_closed")
        self.is_deleted = kwargs.get("is_deleted")
        self.date = kwargs.get("date")
        self.forum_id = kwargs.get("forum")
        self.user_id = kwargs.get("user_id")
        self.user = kwargs.get("user")

    def save(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Threads (
                                              title,
                                              message,
                                              slug,
                                              likes,
                                              dislikes,
                                              points,
                                              isClosed,
                                              isDeleted,
                                              date,
                                              Forums_id,
                                              Users_id,
                                              user)
                              VALUES(%s, %s, %s, 0, 0, 0, %s, %s, %s, %s, %s, %s)""", (
                self.title,
                self.message,
                self.slug,
                self.is_closed,
                self.is_deleted,
                self.date,
                self.forum_id,
                self.user_id,
                self.user)
            )
            self.id = cursor.execute("""SELECT id FROM Threads""")
            connection.commit()
            cursor.close()
            return True
        except IntegrityError:
            connection.rollback()
            cursor.close()
            return False

    def update(self):
        query = """UPDATE Threads SET """
        if self.is_deleted is not None:
            query += """isDeleted = {}, """.format(self.is_deleted)
        if self.is_closed is not None:
            query += """isClosed = {}, """.format(self.is_closed)
        if self.message is not None:
            query += """message = '{}', """.format(self.message)
        if self.slug is not None:
            query += """slug = '{}', """.format(self.slug)
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
    def get_inf(thread_id, include_user=False, include_forum=False):
        cursor = connection.cursor()
        cursor.execute("""SELECT id,
                                 title,
                                 message,
                                 slug,
                                 likes,
                                 dislikes,
                                 points,
                                 isClosed,
                                 isDeleted,
                                 Threads.date,
                                 Forums_id as forum,
                                 Users_id as user,
                                 posts
                                FROM Threads WHERE Threads.id = %s""", (thread_id,))
        result = dictfetch(cursor)
        if not result:
            return None
        result['date'] = result['date'].strftime('%Y-%m-%d %H:%M:%S')
        result['user'] = User.get_inf(include_user, id=result['user'])
        result['forum'] = Forum.get_inf(include_forum, id=result['forum'])
        return result

    @staticmethod
    def list(since, limit, order, **kwargs):
        users_id = kwargs.get('user')
        forum = kwargs.get('forum')
        query = """SELECT t1.id,
                          t1.title,
                          t1.message,
                          t1.slug,
                          t1.likes,
                          t1.dislikes,
                          t1.points,
                          t1.isClosed,
                          t1.isDeleted,
                          t1.date,
                          t1.posts,
                          t2.short_name as forum,
                          t1.user
                         FROM Threads as t1
                         INNER JOIN Forums as t2 ON t1.Forums_id = t2.id """
        if users_id is not None:
            query_param = users_id
            query += """WHERE t1.Users_id = %s """
        elif forum is not None:
            query_param = forum
            query += """WHERE t2.short_name = %s """
        else:
            return None
        if since is not None:
            query += """AND t1.date > '{}' """.format(since)
        query += """ORDER BY t1.date {} """.format(order)
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor = connection.cursor()
        cursor.execute(query, (query_param,))
        result = dictfetchall(cursor)
        cursor.close()
        for item in result:
            item['date'] = item['date'].strftime('%Y-%m-%d %H:%M:%S')
        return result

    @staticmethod
    def list_posts(thread_id, since, limit, order):
        from api.db_service.post_db import Post
        result = Post.list_posts(since, limit, order, thread=thread_id)
        return result

    @staticmethod
    def subscribe(thread_id, email):
        user_id = User.get_inf(email=email)
        if user_id is None:
            return False
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Users_has_Threads (
                                                          Users_id,
                                                          Threads_id
                                                          ) VALUES(%s,%s);""", (user_id, thread_id,))
            connection.commit()
            result = True
        except IntegrityError:
            connection.rollback()
            result = False
        cursor.close()
        return result

    @staticmethod
    def unsubscribe(thread_id, email):
        user_id = User.get_inf(email=email)
        if user_id is None:
            return False
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM Users_has_Threads WHERE Users_id = %s AND Threads_id = %s;""",
                           (user_id, thread_id,))
            connection.commit()
            result = True
        except IntegrityError:
            connection.rollback()
            result = False
        cursor.close()
        return result




# def thread_table(id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT * FROM Threads WHERE id = %s;""", (id,))
#     thread = cursor.fetchall()
#     cursor.close()
#
#     if len(thread) > 0:
#         return thread
#     else:
#         return None
#
#
# def forum_thread(thread_id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT Forums_id FROM Threads WHERE id = %s;""", (thread_id,))
#     forum_id = cursor.fetchall()
#     cursor.close()
#     if len(forum_id) > 0:
#         return get_short_name(forum_id[0][0])
#     else:
#         return None
#
#
# def get_thread_slug(id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT slug FROM Threads WHERE id = %s;""", (id,))
#     thread = cursor.fetchall()
#     cursor.close()
#     if len(thread) > 0:
#         return thread[0][0]
#     else:
#         return None
#
#
# def get_thread_id(slug):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id FROM Threads WHERE slug = %s""", (slug,))
#     thread = cursor.fetchall()
#     cursor.close()
#     if len(thread) > 0:
#         return thread[0][0]
#     else:
#         return None
#
#
# def number_of_posts(thread_id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id FROM Posts WHERE Threads_id = %s""", (thread_id,))
#     result = cursor.fetchall()
#     cursor.close()
#
#     return len(result)
#
#
# def thread_info(thread_id, short_name, include_forum, include_user):
#     thread = thread_table(thread_id)
#     if thread is None:
#         return None
#
#     result = {'date': thread[0][9].strftime('%Y-%m-%d %H:%M:%S'),
#               'dislikes': thread[0][5],
#               'forum': {},
#               'id': thread[0][0],
#               'isClosed': thread[0][7],
#               'isDeleted': thread[0][8],
#               'likes': thread[0][4],
#               'message': thread[0][2],
#               'points': thread[0][6],
#               'posts': number_of_posts(thread_id),
#               'slug': thread[0][3],
#               'title': thread[0][1],
#               'user': {}
#     }
#
#     email = get_user_email_by_id(thread[0][11])
#     if include_user is True:
#         result['user'] = user_info(email)
#     else:
#         result['user'] = email
#     if include_forum is True:
#         result['forum'] = forum_info(short_name, False)
#     else:
#         result['forum'] = short_name
#
#     return result
#
#
# def add_thread(title, message, slug, is_closed, is_deleted, date, forum_id, user_id):
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""INSERT INTO Threads (title, message, slug, likes,
#                           dislikes, points, isClosed, isDeleted,
#                           date, Forums_id, Users_id)
#                           VALUES(%s, %s, %s, 0, 0, 0, %s, %s, %s, %s, %s)""",
#                        (title, message, slug, is_closed, is_deleted, date, forum_id, user_id))
#         connection.commit()
#         cursor.close()
#         return True
#     except IntegrityError:
#         connection.rollback()
#         cursor.close()
#         return False
#
#
# def mark_as_closed(thread_id):
#     cursor = connection.cursor()
#     if get_thread_slug(thread_id) is None:
#         return None
#     try:
#         cursor.execute("""UPDATE Threads SET isClosed = TRUE WHERE id = %s""", (thread_id,))
#         connection.commit()
#         result = thread_id
#     except IntegrityError:
#         connection.rollback()
#         result = None
#     cursor.close()
#     return result
#
#
# def mark_as_open(thread_id):
#     cursor = connection.cursor()
#     if get_thread_slug(thread_id) is None:
#         return None
#     try:
#         cursor.execute("""UPDATE Threads SET isClosed = FALSE WHERE id = %s""", (thread_id,))
#         connection.commit()
#         result = thread_id
#     except IntegrityError:
#         connection.rollback()
#         result = None
#     cursor.close()
#     return result
#
#
# def mark_flag_is_open_in_thread(thread_id, flag):
#     cursor = connection.cursor()
#     if get_thread_slug(thread_id) is None:
#         return None
#     try:
#         cursor.execute("""UPDATE Threads SET isClosed = {}, date=date WHERE id = %s""".format(flag), (thread_id,))
#         connection.commit()
#         result = thread_id
#     except IntegrityError:
#         connection.rollback()
#         result = None
#     cursor.close()
#
#     return result
#
#
# def list_thread_posts(thread_id, since, order, limit):
#     limit = limit_node(limit)
#     since = since_node('date', date_handler(since))
#     slug = get_thread_slug(thread_id)
#     if slug is None:
#         return None
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id FROM Posts
#                       WHERE Threads_id = %s {}
#                       ORDER BY date {}
#                       {}""".format(since, order, limit), (thread_id,))
#     posts = cursor.fetchall()
#     cursor.close()
#     return posts
#
#
# def mark_flag_is_deleted_in_thread(thread_id, flag):
#     cursor = connection.cursor()
#     if get_thread_slug(thread_id) is None:
#         return None
#     try:
#         cursor.execute("""UPDATE Threads SET isDeleted = {}, date=date WHERE id = %s""".format(flag), (thread_id,))
#         connection.commit()
#         result = thread_id
#     except IntegrityError:
#         connection.rollback()
#         result = None
#     cursor.close()
#     return result
#
#
# def subscribe_to_thread(thread_id, email):
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return False
#     slug = get_thread_slug(thread_id)
#     if slug is None:
#         return False
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""INSERT INTO Users_has_Threads (Users_id, Threads_id) VALUES(%s,%s);""", (user_id, thread_id,))
#         connection.commit()
#         result = True
#     except IntegrityError:
#         connection.rollback()
#         result = False
#     cursor.close()
#     return result
#
#
# def unsubscribe_to_thread(thread_id, email):
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return False
#     cursor = connection.cursor()
#     cursor.execute("""SELECT * FROM Users_has_Threads WHERE Users_id = %s AND Threads_id = %s;""",
#                    (user_id, thread_id,))
#     answer = cursor.fetchall()
#     if len(answer) == 0:
#         return False
#     try:
#         cursor.execute("""DELETE FROM Users_has_Threads WHERE Users_id = %s AND Threads_id = %s;""",
#                        (user_id, thread_id,))
#         connection.commit()
#         result = True
#     except IntegrityError:
#         connection.rollback()
#         result = False
#     cursor.close()
#     return result
#
#
# def update_thread(thread_id, message, slug):
#     test = get_thread_slug(thread_id)
#     if test is None:
#         return False
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""UPDATE Threads SET message = %s, slug = %s, date=date WHERE id = %s;""",
#                        (message, slug, thread_id,))
#         connection.commit()
#         result = True
#     except IntegrityError:
#         connection.rollback()
#         result = False
#     cursor.close()
#     return result
#
#
# def vote_thread(thread_id, like, dislike, points):
#     slug = get_thread_slug(thread_id)
#     if slug is None:
#         return False
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""UPDATE Threads SET likes = likes + %s,
#                                              dislikes = dislikes + %s,
#                                              points = points + %s,
#                                              date=date
#                                              WHERE id = %s;""", (like, dislike, points, thread_id,))
#         connection.commit()
#         result = True
#     except IntegrityError:
#         connection.rollback()
#         result = False
#     cursor.close()
#     return result
#
#
#
#
#


