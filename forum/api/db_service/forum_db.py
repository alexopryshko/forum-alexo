from helper import *
from django.db import connection
from django.db import IntegrityError
from api.db_service.user_db import User

__author__ = 'alexander'


class Forum:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.short_name = kwargs.get("short_name")
        self.user = kwargs.get("user")

    def save(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Forums (name, short_name, Users_id)
                              VALUE (%s, %s, %s);""", (self.name, self.short_name, self.user))
            connection.commit()
            result = True
        except IntegrityError:
            connection.rollback()
            result = False
        cursor.close()
        self.fetch()
        return result

    def fetch(self):
        if self.id is not None:
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM Forums WHERE id = %s;""", (self.id,))
        elif self.short_name is not None:
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM Forums WHERE short_name = %s;""", (self.short_name,))
        else:
            return False
        forum = dictfetch(cursor)
        cursor.close()
        if forum:
            self.id = forum.get("id")
            self.name = forum.get("name")
            self.short_name = forum.get("short_name")
            self.user = forum.get("Users_id")
            return True
        else:
            return False

    @staticmethod
    def get_inf(details=False, include_user=False, **kwargs):
        forum_id = kwargs.get("id", None)
        short_name = kwargs.get("forum", None)
        if not details:
            if short_name is not None:
                cursor = connection.cursor()
                cursor.execute("""SELECT id FROM Forums WHERE short_name = %s;""", (short_name,))
                result = dictfetch(cursor)
                if not result:
                    return None
                return result['id']
            if forum_id is not None:
                cursor = connection.cursor()
                cursor.execute("""SELECT short_name FROM Forums WHERE id = %s;""", (forum_id,))
                result = dictfetch(cursor)
                if not result:
                    return None
                return result['short_name']
            else:
                return None
        forum = Forum(short_name=short_name, id=forum_id)
        if not forum.fetch():
            return None
        result = {
            'id': forum.id,
            'name': forum.name,
            'short_name': forum.short_name,
            'user': {}
        }
        if include_user:
            result['user'] = User.get_inf(True, id=forum.user)
        else:
            result['user'] = User.get_inf(id=forum.user)
        return result

    @staticmethod
    def list_users(limit, order, since_id, short_name):
        cursor = connection.cursor()
        # query = """SELECT t1.id,
        #                   t1.username,
        #                   t1.email,
        #                   t1.name,
        #                   t1.isAnonymous,
        #                   t1.about,
        #                   t1.followers,
        #                   t1.following,
        #                   group_concat(t2.Threads_id) as subscriptions
        #                  FROM (
        #                     SELECT t1.id,
        #                            t1.username,
        #                            t1.email,
        #                            t1.name,
        #                            t1.isAnonymous,
        #                            t1.about,
        #                            group_concat(distinct t2.email) as followers,
        #                            group_concat(distinct t3.email) as following FROM Users as t1
        #                       LEFT JOIN Users_has_Users as uhu1 ON t1.id = uhu1.Users_id
        #                       LEFT JOIN Users as t2 ON uhu1.Users_id1 = t2.id
        #
        #                       LEFT JOIN Users_has_Users as uhu2 ON t1.id = uhu2.Users_id1
        #                       LEFT JOIN Users as t3 ON uhu2.Users_id = t3.id
        #                       GROUP BY t1.id
        #                  ) as t1
        #           LEFT JOIN Users_has_Threads as t2 ON t2.Users_id = t1.id
        #           WHERE t1.id IN (SELECT Users_id FROM Posts WHERE forum = %s) """
        query = """SELECT Users_id FROM Posts WHERE forum = %s """
        if since_id is not None:
            query += """ AND Users_id >= {} """.format(since_id)
        query += """ORDER BY Users_id {} """.format(order)
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor.execute(query, (short_name,))
        users = dictfetchall(cursor)
        cursor.close()
        result = [User.get_inf(True, id=user['Users_id']) for user in users]
        # if users:
        #     for item in users:
        #         if item['followers'] is not None:
        #             item['followers'] = item['followers'].split(',')
        #         else:
        #             item['followers'] = []
        #
        #         if item['following'] is not None:
        #             item['following'] = item['following'].split(',')
        #         else:
        #             item['following'] = []
        #
        #         if item['subscriptions'] is not None:
        #             item['subscriptions'] = [int(item_list) for item_list in item['subscriptions'].split(',')]
        #         else:
        #             item['subscriptions'] = []
        # return users
        return result

    @staticmethod
    def list_threads(limit, order, since, short_name, include_user, include_forum):
        forum = Forum.get_inf(True, False, forum=short_name)
        if not forum:
            return None
        cursor = connection.cursor()
        query = """SELECT id,
                          title,
                          message,
                          slug,
                          likes,
                          dislikes,
                          points,
                          isClosed,
                          isDeleted,
                          Threads.date,
                          posts,
                          Forums_id as forum,
                          Users_id as user FROM Threads WHERE Threads.Forums_id = %s """
        if since is not None:
            query += """AND Threads.date > '{}' """.format(since)
        query += """ORDER BY Threads.date {} """.format(order)
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor.execute(query, (forum["id"],))
        result = dictfetchall(cursor)
        cursor.close()
        for item in result:
            item['date'] = item['date'].strftime('%Y-%m-%d %H:%M:%S')
            item['user'] = User.get_inf(include_user, id=item['user'])
            if include_forum:
                item['forum'] = forum
            else:
                item['forum'] = forum['short_name']
        return result

    @staticmethod
    def list_posts(limit, order, since, short_name, include_user, include_forum, include_thread):
        forum = Forum.get_inf(True, False, forum=short_name)
        if not forum:
            return None
        cursor = connection.cursor()
        if include_thread:
            query = """SELECT t1.id as id_p,
                              t1.message as message_p,
                              t1.likes as likes_p,
                              t1.dislikes as dislikes_p,
                              t1.points as points_p,
                              t1.isApproved,
                              t1.isHighlighted,
                              t1.isEdited,
                              t1.isSpam,
                              t1.isDeleted as isDeleted_p,
                              t1.date as date_p,
                              t1.Users_id,
                              t1.parent,

                              t2.id as id_t,
                              t2.title,
                              t2.message as message_t,
                              t2.slug,
                              t2.likes as likes_t,
                              t2.dislikes as dislikes_t,
                              t2.points as points_t,
                              t2.isClosed as isClosed_t,
                              t2.isDeleted as isDeleted_t,
                              t2.date as date_t,
                              t2.user,
                              t2.posts
                             FROM Posts as t1
                             INNER JOIN Threads as t2 ON t1.Threads_id = t2.id
                             WHERE t1.forum = %s """
        else:
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
                              t1.Users_id as user,
                              t1.Threads_id as thread,
                              t1.parent,
                              t1.forum
                             FROM Posts as t1
                             WHERE t1.forum = %s """
        if since is not None:
            query += """AND t1.date > '{}' """.format(since)
        query += """ORDER BY t1.date {} """.format(order)
        if limit is not None:
            query += """LIMIT {}""".format(limit)

        cursor.execute(query, (short_name,))
        buf = dictfetchall(cursor)
        cursor.close()
        if not include_forum:
            forum = forum['short_name']
        if include_thread:
            result = []
            for item in buf:
                result.append(
                    {
                        'id': item['id_p'],
                        'message': item['message_p'],
                        'likes': item['likes_p'],
                        'dislikes': item['dislikes_p'],
                        'points': item['points_p'],
                        'isApproved': item['isApproved'],
                        'isHighlighted': item['isHighlighted'],
                        'isEdited': item['isEdited'],
                        'isSpam': item['isSpam'],
                        'isDeleted': item['isDeleted_p'],
                        'date': item['date_p'].strftime('%Y-%m-%d %H:%M:%S'),
                        'user': User.get_inf(include_user, id=item['Users_id']),
                        'thread': {
                            'id': item['id_t'],
                            'title': item['title'],
                            'message': item['message_t'],
                            'slug': item['slug'],
                            'likes': item['likes_t'],
                            'dislikes': item['dislikes_t'],
                            'points': item['points_t'],
                            'isClosed': item['isClosed_t'],
                            'isDeleted': item['isDeleted_t'],
                            'date': item['date_t'].strftime('%Y-%m-%d %H:%M:%S'),
                            'user': item['user'],
                            'forum': short_name,
                            'posts': item['posts']
                        },
                        'forum': forum,
                        'parent': item['parent']

                    })
            return result
        else:
            for item in buf:
                item['date'] = item['date'].strftime('%Y-%m-%d %H:%M:%S')
                item['user'] = User.get_inf(include_user, id=item['user'])
                item['forum'] = forum
            return buf