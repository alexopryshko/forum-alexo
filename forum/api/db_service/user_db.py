from helper import *
from django.db import connection
from django.db import IntegrityError

__author__ = 'alexander'


class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.email = kwargs.get("email")
        self.about = kwargs.get("about")
        self.name = kwargs.get("name")
        self.username = kwargs.get("username")
        self.is_anonymous = kwargs.get("is_anonymous")
        self.followers = []
        self.following = []
        self.subscriptions = []

    def save(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Users (
                                        username,
                                        email,
                                        name,
                                        isAnonymous,
                                        about
                              ) VALUES (%s, %s, %s, %s, %s);""", (
                self.username, self.email, self.name, self.is_anonymous, self.about)
            )
            connection.commit()
            cursor.close()
        except IntegrityError:
            connection.rollback()
        self.fetch()

    def fetch(self):
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM Users WHERE email = %s; """, (self.email,))
        result = dictfetch(cursor)
        self.id = result.get("id")
        self.email = result.get("email")
        self.about = result.get("about")
        self.name = result.get("name")
        self.username = result.get("username")
        self.is_anonymous = result.get("isAnonymous")
        cursor.close()

    def update(self):
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE Users SET name= %s, about = %s WHERE email = %s""", (
                self.name, self.about, self.email)
            )
            connection.commit()
            result = True
        except IntegrityError:
            connection.rollback()
            result = False
        cursor.close()
        self.fetch()
        return result

    @staticmethod
    def get_inf(details=False, **kwargs):
        user_id = kwargs.get("id", None)
        email = kwargs.get("email", None)
        cursor = connection.cursor()
        if details:
            query = """SELECT  t1.id,
                           t1.username,
                           t1.email,
                           t1.name,
                           t1.isAnonymous,
                           t1.about,
                           t1.followers,
                           t1.following,
                           group_concat(t2.id) as subscriptions
                        FROM (
                                SELECT  t1.id,
                                        t1.username,
                                        t1.email,
                                        t1.name,
                                        t1.isAnonymous,
                                        t1.about,
                                        group_concat(distinct t2.email) as followers,
                                        group_concat(distinct t3.email) as following
                                FROM Users as t1
                                LEFT JOIN Users_has_Users as uhu1 ON t1.id = uhu1.Users_id
                                LEFT JOIN Users as t2 ON uhu1.Users_id1 = t2.id

                                LEFT JOIN Users_has_Users as uhu2 ON t1.id = uhu2.Users_id1
                                LEFT JOIN Users as t3 ON uhu2.Users_id = t3.id
                                GROUP BY t1.id
                        ) as t1
                   LEFT JOIN Threads as t2 ON t2.Users_id = t1.id """

            if user_id is not None:
                query += """WHERE t1.id = %s """
                parameter = user_id
            elif email is not None:
                query += """WHERE t1.email = %s """
                parameter = email
            else:
                return None
            query += """GROUP BY t1.id"""
            cursor.execute(query, (parameter,))
            result = dictfetch(cursor)
            cursor.close()
            if result:
                if result['followers'] is not None:
                    result['followers'] = result['followers'].split(',')
                else:
                    result['followers'] = []

                if result['following'] is not None:
                    result['following'] = result['following'].split(',')
                else:
                    result['following'] = []

                if result['subscriptions'] is not None:
                    result['subscriptions'] = [int(item) for item in result['subscriptions'].split(',')]
                else:
                    result['subscriptions'] = []
                return result
            else:
                return None
        else:
            if email is not None:
                cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
                user_id = cursor.fetchall()
                cursor.close()
                if len(user_id) > 0:
                    return user_id[0][0]
                else:
                    return None
            elif user_id is not None:
                cursor.execute("""SELECT email FROM Users WHERE id = %s; """, (user_id,))
                user_id = cursor.fetchall()
                cursor.close()
                if len(user_id) > 0:
                    return user_id[0][0]
                else:
                    return None
            else:
                return None

    @staticmethod
    def follow(follower, followee):
        follower_id = User.get_inf(email=follower)
        if follower_id is None:
            return None
        followee_id = User.get_inf(email=followee)
        if followee_id is None:
            return None
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Users_has_Users (Users_id, Users_id1)
                                 VALUES (%s, %s);""", (followee_id, follower_id))
            connection.commit()
        except IntegrityError:
            connection.rollback()
        cursor.close()
        return User.get_inf(True, id=follower_id)

    @staticmethod
    def unfollow(follower, followee):
        follower_id = User.get_inf(email=follower)
        if follower_id is None:
            return None
        followee_id = User.get_inf(email=followee)
        if followee_id is None:
            return None
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM Users_has_Users WHERE
                              users_id = %s AND users_id1 = %s""", (followee_id, follower_id))
            connection.commit()
        except IntegrityError:
            connection.rollback()
        cursor.close()
        return User.get_inf(True, id=follower_id)

    #todo: optimize
    @staticmethod
    def list_followers(limit, order, since_id, email):
        user_id = User.get_inf(email=email)
        if user_id is None:
            return None
        cursor = connection.cursor()
        query = """SELECT  t1.id,
                                  t1.username,
                                  t1.email,
                                  t1.name,
                                  t1.isAnonymous,
                                  t1.about,
                                  t1.followers,
                                  t1.following,
                                  group_concat(t2.id) as subscriptions
                                 FROM (
                                    SELECT  t1.id,
                                            t1.username,
                                            t1.email,
                                            t1.name,
                                            t1.isAnonymous,
                                            t1.about,
                                            group_concat(distinct t2.email) as followers,
                                            group_concat(distinct t3.email) as following
                                           FROM Users as t1
                                            LEFT JOIN Users_has_Users as uhu1 ON t1.id = uhu1.Users_id
                                            LEFT JOIN Users as t2 ON uhu1.Users_id1 = t2.id

                                            LEFT JOIN Users_has_Users as uhu2 ON t1.id = uhu2.Users_id1
                                            LEFT JOIN Users as t3 ON uhu2.Users_id = t3.id
                                            WHERE uhu2.Users_id = %s
                                            GROUP BY t1.id
                                ) as t1
                                LEFT JOIN Threads as t2 ON t2.Users_id = t1.id """
        if since_id is not None:
            query += """WHERE t1.id > {} """.format(since_id)
        if order is not None:
            query += """GROUP BY t1.id ORDER BY t1.name {} """.format(order)
        else:
            query += """GROUP BY t1.id ORDER BY t1.name DESC """
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor.execute(query, (user_id,))
        followers = dictfetchall(cursor)
        cursor.close()
        if followers:
            for item in followers:
                if item['followers'] is not None:
                    item['followers'] = item['followers'].split(',')
                else:
                    item['followers'] = []

                if item['following'] is not None:
                    item['following'] = item['following'].split(',')
                else:
                    item['following'] = []

                if item['subscriptions'] is not None:
                    item['subscriptions'] = [int(item_list) for item_list in item['subscriptions'].split(',')]
                else:
                    item['subscriptions'] = []
        return followers

    @staticmethod
    def list_following(limit, order, since_id, email):
        user_id = User.get_inf(email=email)
        if user_id is None:
            return None
        cursor = connection.cursor()
        query = """SELECT  t1.id,
                                  t1.username,
                                  t1.email,
                                  t1.name,
                                  t1.isAnonymous,
                                  t1.about,
                                  t1.followers,
                                  t1.following,
                                  group_concat(t2.id) as subscriptions
                                 FROM (
                                    SELECT  t1.id,
                                            t1.username,
                                            t1.email,
                                            t1.name,
                                            t1.isAnonymous,
                                            t1.about,
                                            group_concat(distinct t2.email) as followers,
                                            group_concat(distinct t3.email) as following
                                           FROM Users as t1
                                            LEFT JOIN Users_has_Users as uhu1 ON t1.id = uhu1.Users_id
                                            LEFT JOIN Users as t2 ON uhu1.Users_id1 = t2.id

                                            LEFT JOIN Users_has_Users as uhu2 ON t1.id = uhu2.Users_id1
                                            LEFT JOIN Users as t3 ON uhu2.Users_id = t3.id
                                            WHERE uhu1.Users_id1 = %s
                                            GROUP BY t1.id
                                ) as t1
                                LEFT JOIN Threads as t2 ON t2.Users_id = t1.id """
        if since_id is not None:
            query += """WHERE t1.id > {} """.format(since_id)
        if order is not None:
            query += """GROUP BY t1.id ORDER BY t1.name {} """.format(order)
        else:
            query += """GROUP BY t1.id ORDER BY t1.name DESC """
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor.execute(query, (user_id,))
        following = dictfetchall(cursor)
        cursor.close()
        if following:
            for item in following:
                if item['followers'] is not None:
                    item['followers'] = item['followers'].split(',')
                else:
                    item['followers'] = []

                if item['following'] is not None:
                    item['following'] = item['following'].split(',')
                else:
                    item['following'] = []

                if item['subscriptions'] is not None:
                    item['subscriptions'] = [int(item_list) for item_list in item['subscriptions'].split(',')]
                else:
                    item['subscriptions'] = []
        return following

    @staticmethod
    def list_posts(email, since, limit, order):
        #since = since_node("date", date_handler(since))
        #limit = limit_node(limit)
        #user_id = User.get_inf(email)
        #if user_id is None:
        #    return None

        query = """SELECT t1.date,
                          t1.dislikes,
                          t1.forum,
                          t1.id,
                          t1.isApproved,
                          t1.isDeleted,
                          t1.isEdited,
                          t1.isHighlighted,
                          t1.isSpam,
                          t1.likes,
                          t1.message,
                          t1.parent,
                          t1.points,
                          t1.Threads_id as thread,
                          t2.email as user
                         FROM Posts as t1
                         INNER JOIN Users as t2 ON t2.id = t1.Users_id
                         WHERE t2.email = %s """
        if since is not None:
            query += """AND t1.date > '{}' """.format(since)
        if order is not None:
            query += """ORDER BY t1.date {} """.format(order)
        else:
            query += """ORDER BY t1.date DESC """
        if limit is not None:
            query += """LIMIT {}""".format(limit)
        cursor = connection.cursor()
        cursor.execute(query, (email,))
        posts = dictfetchall(cursor)
        if posts:
            for item in posts:
                item['date'] = item['date'].strftime('%Y-%m-%d %H:%M:%S')
        cursor.close()
        return posts

#
# def get_user_email_by_id(user_id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT email FROM Users WHERE id = %s; """, (user_id,))
#     email = cursor.fetchall()
#     cursor.close()
#     if len(email) > 0:
#         return email[0][0]
#     else:
#         return None
#
# def get_user_id_by_email(email):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
#     id = cursor.fetchall()
#     cursor.close()
#     if len(id) > 0:
#         return id[0][0]
#     else:
#         return None
#
# def user_table(email):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT * FROM Users WHERE email = %s; """, (email,))
#     result = cursor.fetchall()
#     cursor.close()
#     if len(result) > 0:
#         return result
#     else:
#         return None
#
# def user_subscriptions(user_id):
#     cursor = connection.cursor()
#     cursor.execute("""SELECT Threads_id FROM Users_has_Threads WHERE Users_id = %s""", (user_id,))
#     threads = cursor.fetchall()
#     cursor.close()
#     result = []
#     for thread in threads:
#         result.append(thread[0])
#     return result
#
# def user_info(email):
#     result = user_table(email)
#     if result is None:
#         return None
#
#     cursor = connection.cursor()
#     cursor.execute("""SELECT t2.email FROM Users AS t1
#                           INNER JOIN Users_has_Users AS t ON t.Users_id = t1.id
#                           INNER JOIN Users AS t2 ON t.Users_id1 = t2.id
#                           WHERE t1.email = %s AND t1.id != t2.id""", (email,))
#     followers = cursor.fetchall()
#     if len(followers) > 0:
#         followers = followers[0]
#
#     cursor.execute("""SELECT t2.email FROM Users AS t1
#                                   INNER JOIN Users_has_Users AS t ON t.Users_id1 = t1.id
#                                   INNER JOIN Users AS t2 ON t.Users_id = t2.id
#                                   WHERE t1.email = %s AND t1.id != t2.id""", (email,))
#     following = cursor.fetchall()
#     if len(following) > 0:
#         following = following[0]
#
#     result = {'about': result[0][5],
#               'email': result[0][2],
#               'followers': followers,
#               'following': following,
#               'id': result[0][0],
#               'isAnonymous': result[0][4],
#               'name': result[0][3],
#               'subscriptions': user_subscriptions(result[0][0]),
#               'username': result[0][1]}
#     cursor.close()
#     return result
#
# def information_about_user(user_id, flag):
#     email = get_user_email_by_id(user_id)
#     if flag:
#         return user_info(email)
#     else:
#         return email
#
# def add_user(username, email, name, isAnonymous, about):
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""INSERT INTO Users (username, email, name, isAnonymous, about)
#                           VALUES (%s, %s, %s, %s, %s);""", (username, email, name, isAnonymous, about))
#         connection.commit()
#         cursor.close()
#         return True
#     except IntegrityError:
#         connection.rollback()
#         cursor.close()
#         return False
#
# def subscribe(follower, followee):
#
#     follower_id = get_user_id_by_email(follower)
#     if follower_id is None:
#         return None
#
#     followee_id = get_user_id_by_email(followee)
#     if followee_id is None:
#         return None
#
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""INSERT INTO Users_has_Users (Users_id, Users_id1)
#                              VALUES (%s, %s);""", (followee_id, follower_id))
#         connection.commit()
#     except IntegrityError:
#         connection.rollback()
#
#     cursor.close()
#     return user_info(follower)
#
# def unsubscribe(follower, followee):
#     follower_id = get_user_id_by_email(follower)
#     if follower_id is None:
#         return None
#
#     followee_id = get_user_id_by_email(followee)
#     if followee_id is None:
#         return None
#     cursor = connection.cursor()
#     try:
#         cursor.execute("""DELETE FROM Users_has_Users WHERE
#                           users_id = %s AND users_id1 = %s""", (followee_id, follower_id))
#         connection.commit()
#     except IntegrityError:
#         connection.rollback()
#
#     cursor.close()
#     return user_info(follower)
#
# def list_followers(limit, order, since_id, email):
#     limit = limit_node(limit)
#     cursor = connection.cursor()
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return None
#     cursor.execute("""SELECT t2.email FROM Users AS t1
#                           INNER JOIN Users_has_Users AS t ON t.Users_id = t1.id
#                           INNER JOIN Users AS t2 ON t.Users_id1 = t2.id
#                           WHERE t1.id = %s AND t1.id != t2.id AND t2.id >= {}
#                           ORDER BY t2.name {}
#                           {}""".format(since_id, order, limit), (user_id, ))
#     followers = cursor.fetchall()
#     cursor.close()
#     return followers
#
# def list_following(limit, order, since_id, email):
#     limit = limit_node(limit)
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return None
#     cursor = connection.cursor()
#     cursor.execute("""SELECT t2.email FROM Users AS t1
#                           INNER JOIN Users_has_Users AS t ON t.Users_id1 = t1.id
#                           INNER JOIN Users AS t2 ON t.Users_id = t2.id
#                           WHERE t1.id = %s AND t1.id != t2.id AND t2.id >= {}
#                           ORDER BY t2.name {}
#                           {}""".format(since_id, order, limit), (user_id, ))
#     following = cursor.fetchall()
#     cursor.close()
#     return following
#
# def update(name, about, email):
#     cursor = connection.cursor()
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return None
#     try:
#         cursor.execute("""UPDATE Users SET name= %s, about = %s WHERE id= %s""", (name, about, user_id))
#         connection.commit()
#         result = user_info(email)
#     except IntegrityError:
#         connection.rollback()
#         result = None
#     cursor.close()
#     return result
#
# def thread_created_by_user(email, since, order, limit):
#     since = since_node('date', date_handler(since))
#     limit = limit_node(limit)
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return None
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id FROM Threads
#                       WHERE Users_id = %s {}
#                       ORDER BY date {}
#                       {}""".format(since, order, limit), (user_id, ))
#     threads = cursor.fetchall()
#     cursor.close()
#     return threads
#
# def post_created_by_user(email, since, limit, order):
#     since = since_node("date", date_handler(since))
#     limit = limit_node(limit)
#     user_id = get_user_id_by_email(email)
#     if user_id is None:
#         return None
#
#     cursor = connection.cursor()
#     cursor.execute("""SELECT id FROM Posts WHERE Users_id = %s {}
#                       ORDER BY date {}
#                       {}""".format(since, order, limit), (user_id,))
#     posts = cursor.fetchall()
#     cursor.close()
#     return posts
#
