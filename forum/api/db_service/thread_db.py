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
        self.posts = kwargs.get("posts")
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
            query += """points = points + {}, """.format(self.points)
        if self.posts is not None:
            query += """posts = posts + {}, """.format(self.posts)
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

    #todo
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
