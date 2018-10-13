#!/usr/bin/env python

import cgi
import psycopg2
import psycopg2.extras
import config

def eventList():
    conn = psycopg2.connect(config.dbconn);
    cur = conn.cursor()
    cur.execute("select id, name from event where active = 't' order by start_time")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return events


print "Content-Type: text/html" 
print


print """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
<title>len.ro - Active Tracker</title>
<link href="generator.css" rel="stylesheet" type="text/css"/>
</head>
<body>
<script type="text/javascript" src="jquery-1.6.1.min.js"></script>
<script type="text/javascript" src="generator.js"></script>
<h1><img src="logo.png" align="absmiddle"/>ActiveTracker embed code generator</h1>
<h2>1. Select the event</h2>
<select id="event">
<option value="0">--</option>
"""

dataSource = eventList()
for event in dataSource: 
    print '<option value="%s">%s</option>' % (event[0], event[1])

print """
</select>
<br/>
<h2>2. Preview</h2>
<div id="preview">
</div>
<br/>
<h2>3. Copy embed code</h2>
<div id="description">Copy the code below into your html page
</div>
<textarea id="code">
</textarea>
</body>
</html>
"""

