import MySQLdb
__author__ = 'alexander'

def get_connect():
    db = MySQLdb.connect(host="localhost", user="AlexO", passwd="pwd", db="tp_project_forum")
    return db
