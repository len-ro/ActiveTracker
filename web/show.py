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

def getMsgUpdate(cur, init, eventId):
    sql = """select m.trackcode as trackcode, m.external_time as time, m.cp as cp, m.lap as lap, m.rank as rank, m.msg as msg from event_msg m where m.event_fk = %(eventId)s and date_trunc('day', m.update_time) = current_date and m.trackCode in (select distinct(trackCode) from position where event_fk = %(eventId)s) and m.update_time = (select max(m2.update_time) from event_msg m2 where m2.trackcode = m.trackcode and m2.event_fk = m.event_fk)"""
    params = {'eventId':eventId}
    if init:
        sql = sql + """ and m.update_time at time zone 'UTC' > %(t)s """
        params['t'] = init
    sql = sql + """ order by update_time asc"""
    cur.execute(sql, params)
    results = cur.fetchall()
    out = ""
    for res in results:
        trackCode = res['trackcode']
        time = str(res['time'])[:8]
        out = out + """<msg trackCode="%s" time="%s" """ % (trackCode, time)
        for k in ['cp', 'lap', 'rank', 'msg']:
            if res[k]:
                out = out + '%s="%s" ' % (k, res[k])
        out = out + '/>\n'
    return out

def getPositionUpdate(cur, init, eventId, lastOnly):
    sql = """select p.trackcode as trackcode, p.lat as lat, p.lon as lon, p.alt as alt, p.update_time at time zone 'UTC' as ut from position p where p.event_fk = %(eventId)s and date_trunc('day', p.update_time) = current_date """
    params = {'eventId':eventId}
    if init:
        sql = sql + """and p.update_time at time zone 'UTC' > %(t)s """
        params['t'] = init
    if lastOnly:
        sql = sql + """ and p.update_time = (select max(t2.update_time) from position t2 where t2.trackcode = p.trackcode and t2.event_fk = %(eventId)s) """
    sql = sql + """ order by update_time asc""" 
    cur.execute(sql, params)
    results = cur.fetchall()
    out = ""
    for res in results:
        trackCode = res['trackcode']
        lat = res['lat']
        lon = res['lon']
        alt = res['alt']
        gps_time = str(res['ut'])[:19]        
        out = out + """<loc trackCode="%s" lat="%s" lon="%s" alt="%s" t="%s"/>\n""" % (trackCode, lat, lon, alt, gps_time)
    return out

def getUpdate(init, trackCode, eventId, lastOnly):
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    out = '<track>\n'
    out = out + getMsgUpdate(cur, init, eventId)
    out = out + getPositionUpdate(cur, init, eventId, lastOnly)
    out = out + '</track>\n'
    conn.commit()
    cur.close()
    conn.close()
    return out

form = cgi.FieldStorage()
trackCode = form.getvalue('trackCode', None)
init = form.getvalue('t', None)
eventId = form.getvalue('eventId', None)
lastOnly = form.getvalue('lastOnly', None)

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/xml"
print

print getUpdate(init, trackCode, eventId, lastOnly)
