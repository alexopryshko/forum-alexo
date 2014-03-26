import MySQLdb
__author__ = 'alexander'

db = MySQLdb.connect(host="localhost", user="AlexO", passwd="pwd", db="tp_project_forum")

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
              'username': resExec[0][1]}
    cursor.close()
    return result

def informationAboutUser(user_id, flag):
    email = getUserEmailByID(user_id)
    if flag:
        return user_info(email)
    else:
        return email

def getUserEmailByID(user_id):
    cursor = db.cursor()
    cursor.execute("""SELECT email FROM Users WHERE id = %s; """, (user_id,))
    email = cursor.fetchall()
    print email
    cursor.close()
    return email

def getUserIDByEmail(email):
    cursor = db.cursor()
    cursor.execute("""SELECT id FROM Users WHERE email = %s; """, (email,))
    id = cursor.fetchall()
    if len(id) > 0:
        return id
    else:
        return None