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

def getMsgUpdate(cur, eventId, init, delta):
    sql = """select m.trackcode as trackcode, m.external_time as time, m.cp as cp, m.lap as lap, m.rank as rank, m.msg as msg from event_msg m where m.event_fk = %(eventId)s and m.trackCode in (select distinct(trackCode) from position where event_fk = %(eventId)s)"""
    params = {'eventId':eventId, 'delta':delta}

    if not init:
        sql = sql + """ and m.update_time >= (select start_time from event where id = %(eventId)s) and m.update_time < ((select start_time from event where id = %(eventId)s) + interval '%(delta)s seconds')""" 
    else:
        sql = sql + """ and m.update_time at time zone 'UTC' > %(t)s and m.update_time at time zone 'UTC' < timestamp %(t)s + interval '%(delta)s seconds'"""
        params['t'] = init

    sql = sql + """ order by m.update_time asc"""
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

def getPositionUpdate(cur, eventId, init, delta):
    sql = """select p.trackcode as trackcode, p.lat as lat, p.lon as lon, p.alt as alt, p.update_time at time zone 'UTC' as ut from position p where p.event_fk = %(eventId)s """
    params = {'eventId':eventId, 'delta':delta}

    if not init:
        sql = sql + """ and p.update_time >= (select start_time from event where id = %(eventId)s) and p.update_time < ((select start_time from event where id = %(eventId)s) + interval '%(delta)s seconds')""" 
    else:
        sql = sql + """ and p.update_time at time zone 'UTC' > %(t)s and p.update_time at time zone 'UTC' < timestamp %(t)s + interval '%(delta)s seconds'"""
        params['t'] = init
        
    sql = sql + """ order by p.update_time asc""" 
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

def getReplay(eventId, init, delta):
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    out = '<track>\n'
    out = out + getMsgUpdate(cur, eventId, init, delta)
    out = out + getPositionUpdate(cur, eventId, init, delta)
    out = out + '</track>\n'
    conn.commit()
    cur.close()
    conn.close()
    return out

form = cgi.FieldStorage()
init = form.getvalue('t', None)
eventId = form.getvalue('eventId', None)
delta = form.getvalue('d', '15')

if not re.match('^[-]?[0-9]{1,4}$', delta):
    delta = '15'

delta = int(delta)
if (delta < -1800) or (delta > 1800):
    delta = 15

#2013-06-09 07:00:01
#init = datetime.datetime.strptime(init, '%Y-%m-%d %H:%M:%S') 

#TODO more verification of params integrity

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/xml"
print

print getReplay(eventId, init, delta)
