#!/usr/bin/env python

import cgi
import cgitb
cgitb.enable()
#cgitb.enable(display=0, logdir="/var/log/apache2/trackme")
import datetime
import psycopg2
import re
import json

#configuration
from config import dbconn

tCodes = [
    ('eventId', '^[0-9]{,4}$', None, None), 
    ('trackCode', '^[0-9]{,3}$', None, None), 
    ('lat', '^[0-9]{,3}[\.,][0-9]{,7}$', None, 'cleanNo'), 
    ('lon', '^[0-9]{,3}[\.,][0-9]{,7}$', None, 'cleanNo'), 
    ('alt', '^[0-9]{,4}([\.,][0-9]{,7})?$', '0', 'cleanNo'), 
    ('accuracy', '^-?[0-9]{,5}([.,][0-9]{,4})?$', '-1', 'cleanNo'), 
    ('time', '^[0-9]{,14}$', None, 'cleanTime')
]

def store_update(phoneId, tData): 
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor()
    
    if phoneId:
        cur.execute("""insert into event_phone(event_fk, trackCode, phone_id) values (%s, %s, %s)""", (tData['eventId'], tData['trackCode'], phoneId))

    cur.execute("""select current_timestamp > start_time and current_timestamp < end_time from event where id = %s""", (tData['eventId'],))
    results = cur.fetchall()
    started = results[0][0]
    if started:
        cur.execute("""insert into position(event_fk, trackCode, lat, lon, alt, accuracy, gps_time) values (%s, %s, %s, %s, %s, %s, %s)""", (tData['eventId'], tData['trackCode'], tData['lat'], tData['lon'], tData['alt'], tData['accuracy'], tData['time']))
    else:
        pass
        #print 'Not started'
        
    conn.commit()
    cur.close()
    conn.close()

def cleanNo(no):
    return no.replace(',', '.')

def cleanTime(t):
    return datetime.datetime.fromtimestamp(float(t)/1000)

"""
New/shorter format parsing
"""
def parseT(t):
    tv = t.split('|')
    tData = {}
    i = 0
    for k in tCodes:
        if i >= len(tv):
            return (False, 'invalid length')
            break
        v = tv[i]
        if not re.match(k[1], v):
            return (False, 'not match: ' + k[0] + ', ' + v)
        else:
            if k[3]:
                v = globals()[k[3]](v)
            tData[k[0]] = v
        i = i + 1

    return (True, tData)

"""
Old format parsing
"""
def parseOld(form):
    tData = {}
    for k in tCodes:
        v = form.getvalue(k[0], k[2])
        
        if not v:
            return (False, 'mising: ' + k[0])
        elif not re.match(k[1], v):
            return (False, 'not match: ' + k[0] + ', ' + v)
        else:
            if k[3]:
                v = globals()[k[3]](v)
            tData[k[0]] = v
    return (True, tData)

def parse():
    form = cgi.FieldStorage()
    out = None
    u = None
    phoneId = form.getvalue('phoneId', None)
    t = form.getvalue('t', None)
    if t:
        u = parseT(t)
    else:
        u = parseOld(form)
    
    if u[0]:
        store_update(phoneId, u[1])
    return u[1]

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/json"
print

print parse()
