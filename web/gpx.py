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

gpxH = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:rmc="urn:net:trekbuddy:1.0:nmea:rmc" creator="ActiveTracker v0.2 http://www.len.ro/" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www.garmin.com/xmlschemas/WaypointExtensionv1.xsd" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
 <metadata>
  <time>2013-05-31T11:03:49Z</time>
 </metadata>
 <trk>
  <name>%(name)s</name>
"""

gpxF="""</trk>
</gpx>"""

def getGpx(eventId, trackCode):
    conn = psycopg2.connect(dbconn);
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """select p.trackcode as trackcode, p.lat as lat, p.lon as lon, p.alt as alt, p.update_time at time zone 'UTC' as ut from position p where p.event_fk = %(eventId)s and p.trackcode = %(trackCode)s order by p.update_time asc"""
    params = {'eventId':eventId, 'trackCode':trackCode}

    cur.execute(sql, params)

    out = gpxH % {'name':'Marvin50km-Len'}
    out = out + '<trkseg>\n'
    results = cur.fetchall()
    for res in results:
        trackCode = res['trackcode']
        lat = res['lat']
        lon = res['lon']
        alt = res['alt']
        time = res['ut'].isoformat()        
        out = out + """<trkpt lat="%(lat)s" lon="%(lon)s">
<ele>%(alt)s</ele>
<time>%(time)s</time>
</trkpt>\n""" % { 'lat': lat, 'lon': lon, 'alt': alt, 'time':time }
    out = out + '</trkseg>\n'
    out = out + gpxF
    conn.commit()
    cur.close()
    conn.close()
    return out

form = cgi.FieldStorage()
trackCode = form.getvalue('trackCode', None)
eventId = form.getvalue('eventId', None)

print "Cache-Control: no-cache, max-age=0, must-revalidate, no-store"
print "Pragma: no-cache"
print "Content-type: text/xml"
print

print getGpx(eventId, trackCode)
