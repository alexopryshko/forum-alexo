__author__ = 'alexander'


def limit_node(limit):
    if limit == "":
        return ""
    return " LIMIT " + limit

def since_node(table, since):
    if since == "":
        return ""
    return " AND " + table + " > " + since