#!/usr/bin/env python

import cgi
import cgitb
cgitb.enable()
#cgitb.enable(display=0, logdir="/tmp/")
import datetime
import psycopg2
import psycopg2.extras
import json
import re

#configuration
from config import dbconn

def getUserInfo(eventId):
    users = {}
    if eventId:
        conn = psycopg2.connect(dbconn);
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = """select trackCode, label, color, shortname, pin from event_user where event_fk = %(eventId)s"""
        params = {'eventId': eventId}
        cur.execute(sql, params)

        results = cur.fetchall()

        for res in results:
            asDict = dict(res);
            users[asDict['trackcode']] = asDict

        conn.commit()
        cur.close()
        conn.close()
    return json.dumps(users, indent=4)

form = cgi.FieldStorage()
eventId = form.getvalue('eventId', None)
if not re.match('^[0-9]{,3}$', eventId):
    eventId = None

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/json"
print

print getUserInfo(eventId)
