#!/usr/bin/env python

import cgi
import cgitb
cgitb.enable()
#cgitb.enable(display=0, logdir="/var/log/apache2/trackme")
import datetime
import psycopg2

#configuration
from config import dbconn

def store_update(eventId, trackCode, lat, lon, alt, gps_time):    
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor()
    cur.execute("""insert into position(event_fk, trackCode, lat, lon, alt, gps_time) values (%s, %s, %s, %s, %s, %s)""", (eventId, trackCode, lat, lon, alt, gps_time))
    conn.commit()
    cur.close()
    conn.close()

def cleanNo(no):
    return no.replace(',', '.')

form = cgi.FieldStorage()
id = form.getvalue('id', None)
trackCode = form.getvalue('trackCode', None)
eventId = form.getvalue('eventId', None)
lat = cleanNo(form.getvalue('lat', None))
lon = cleanNo(form.getvalue('lon', None))
alt = cleanNo(form.getvalue('alt', None))

debug = False
if form.has_key('debug'):
    debug = True
gps_time = datetime.datetime.fromtimestamp(float(form['time'].value)/1000)

store_update(eventId, trackCode, lat, lon, alt, gps_time)

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/xml"
print

if debug:
    print """<track><loc trackCode="%s" lat="%s" long="%s" alt="%s" time="%s"/></track>""" % (trackCode, lat, lon, alt, gps_time)
else:
    print '<track/>'
