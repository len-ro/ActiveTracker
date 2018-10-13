#!/usr/bin/env python

import cgi
import cgitb
cgitb.enable()
#cgitb.enable(display=0, logdir="/tmp/")
import psycopg2
import psycopg2.extras
import re

#configuration
from config import dbconn

def getWidgetPage(eventId, replay, init, debug):
    jsCode = 'trackme.min.js'
    if debug:
        jsCode = 'trackme.js'

    out = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <!--<script type="text/javascript" src="https://getfirebug.com/firebug-lite.js"></script>-->
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>len.ro - Active Tracker</title>
    <link href="trackme.css" rel="stylesheet" type="text/css"/>
    <link href="jquery.countdown.css" rel="stylesheet" type="text/css"/>
  </head>
  <body>
    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
    <script type="text/javascript" src="jquery-1.6.1.min.js"></script>
    <script type="text/javascript" src="jquery.timers-1.2.js"></script>
    <script type="text/javascript" src="jquery.blockUI.js"></script>
    <script type="text/javascript" src="jquery.countdown.min.js"></script>
    <script type="text/javascript" src="tinycolor.js"></script>
    <script type="text/javascript">
       var eventId = %(eventId)s;
       var replay = %(replay)s;
       var init = %(init)s;
    </script>
    <script type="text/javascript" src="%(jsCode)s"></script>
    <div id="header">
      <h1 id="title"><a href="http://www.len.ro/cycling/activetracker/">&copy;2013 len.ro ActiveTracker</a>: <span id="eventName"></span></h1>
      <div id="category">Tracking: <select id="categories" disabled></select></div>
    </div>
    <div id="wrapper">
    <div id="content">
    <div id="map"></div>
    </div>
    </div>
    <div id="footer">&copy; 2013 len.ro</div>
  </body>
</html>""" % {'eventId': eventId, 'replay': replay, 'init': init, 'jsCode': jsCode}
    return out

def safeEventId(eventId, defEventId):
    if not eventId:
        return defEventId

    if not re.match('^[0-9]+$', eventId):
        return defEventId

    conn = psycopg2.connect(dbconn);
    cur = conn.cursor()
    cur.execute("select count(*) from event where id = %(eventId)s", {'eventId': eventId})
    results = cur.fetchall()
    if results[0][0] == 0:
        eventId = defEventId
    conn.commit()
    cur.close()
    conn.close()
    return eventId

form = cgi.FieldStorage()
eventId = form.getvalue('eventId', None)
eventId = safeEventId(eventId, '8') #TODO defaults to Active Test event

replay = form.getvalue('replay', 'f')

if replay == 't':
    replay = 'true'
else:
    replay = 'false'

width = form.getvalue('width', 600)
height = form.getvalue('height', 500)

init = form.getvalue('init', 'f')
if init == 't':
    init = 'true'
else:
    init = 'false'

debug = form.getvalue('debug', 'f')
if debug == 't':
    debug = 'true'
else:
    debug = 'false'


print "Content-type: text/html"
print

print getWidgetPage(eventId, replay, init, debug)
