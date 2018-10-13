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

#msg.py?trackCode=101&time=200000&cp=1&lap=1&position=2

tCodes = [
    ('trackCode', '^[0-9]{,3}$', True, None, None), 
    ('time', '^[0-9]{6}$', True, None, None),
    ('cp', '^[a-zA-Z0-9]{,7}$', True, None, None), 
    ('lap', '^[0-9]{,2}$', False, None, None), 
    ('position', '^[0-9]{,3}$', False, None, None), 
    ('eventId', '^[0-9]{,3}$', True, None, None),
    ('msg', '^[0-9a-zA-Z ]{,128}', False, None, None)
]

def storeUpdate(tData): 
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor()
    
    cur.execute("""select current_timestamp > start_time and current_timestamp < end_time from event where id = %s""", (tData['eventId'],))
    results = cur.fetchall()
    started = results[0][0]
    if started:
        cur.execute("""insert into event_msg(event_fk, trackCode, external_time, cp, lap, rank, msg) values (%s, %s, %s, %s, %s, %s, %s)""", (tData['eventId'], tData['trackCode'], tData['time'], tData['cp'], tData['lap'], tData['position'], tData['msg']))
        msg = [True]
    else:
        msg = [False, 'Event not started']
        
    conn.commit()
    cur.close()
    conn.close()
    return msg

def cleanNo(no):
    return no.replace(',', '.')

def parseForm(form):
    tData = {}
    for k in tCodes:
        v = form.getvalue(k[0], k[3])
        
        if k[2] and v == None:
            return (False, 'missing: ' + k[0])
        if not v == None:
            if not re.match(k[1], v):
                return (False, k[0] + ' does not match: ' + k[1] + ', ' + v)
            else:
                if k[4]:
                    v = globals()[k[4]](v)
        tData[k[0]] = v
    return (True, tData)

def parse():
    form = cgi.FieldStorage()
    u = parseForm(form)
    
    if u[0]:
        return storeUpdate(u[1])
    return u

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/json"
print

print json.dumps(parse())
