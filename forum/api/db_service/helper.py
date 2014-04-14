__author__ = 'alexander'


def limit_node(limit):
    if limit == "":
        return ""
    return " LIMIT " + limit


def since_node(table, since):
    if since == "''":
        return ""
    return " AND " + table + " > " + since


def date_handler(date):
    return "'" + date + "'"


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def dictfetch(cursor):
    desc = cursor.description
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(zip([col[0] for col in desc], row))