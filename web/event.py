#!/usr/bin/env python

import cgi
import cgitb
cgitb.enable()
#cgitb.enable(display=0, logdir="/tmp/")
import datetime
import psycopg2
import psycopg2.extras
import json

#configuration
from config import dbconn

def getEventInfo(eventId):
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """select id, event_index, name, code, parent_fk, logo, start_time at time zone 'UTC' as start_time, end_time at time zone 'UTC' as end_time, kml_file, map_type, map_center_lat, map_center_lon, refresh_interval, draw_path, view_bounds, youtube, msg from event """
    params = None
    if eventId:
        sql = sql + """where (id = %(eventId)s or parent_fk = %(eventId)s)"""
        params = {'eventId': eventId}
    else:
        sql = sql + """where active = 't'"""

    sql = sql + ' order by parent_fk nulls first, event_index'
    cur.execute(sql, params)
    events = []
    results = cur.fetchall()

    for res in results:
        res['start_time'] = str(res['start_time'])
        res['end_time'] = str(res['end_time'])
        parent_fk = res['parent_fk']
        if not parent_fk:
            events.append(dict(res))
        else:
            foundParent = False
            for e in events:
                if e['id'] == parent_fk:
                    foundParent = True
                    if not e.has_key('events'):
                        e['events'] = []
                    e['events'].append(dict(res))
            if not foundParent:
                events.append(dict(res))
    out = json.dumps(events, indent=4)
    conn.commit()
    cur.close()
    conn.close()
    return out

form = cgi.FieldStorage()
eventId = form.getvalue('eventId', None)

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/json"
print

print getEventInfo(eventId)
