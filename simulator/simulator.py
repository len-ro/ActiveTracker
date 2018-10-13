#!/usr/bin/env python

import sys
import time
import random
import urllib2
import threading
import re

class userThread (threading.Thread):
    def __init__(self, eventId, trackCode, data):
        threading.Thread.__init__(self)
        self.eventId = eventId
        self.trackCode = trackCode
        self.data = data

    def run(self):
        print "Starting " + self.trackCode
        device(self.eventId, self.trackCode, self.data)
        print "Exiting " + self.trackCode

def device(eventId, trackcode, data):
    wait = random.randint(1, 5)
    time.sleep(wait)
    for p in data:
        now = time.time()
        url = 'http://www.len.ro/activeTracker/trackMe.py?t=%s|%s|%s|%s|0|0|%s' % (eventId, trackcode, p[1], p[0], int(now*1000))
        print url
        data = urllib2.urlopen(url).read()
        print data
        wait = random.randint(1, 10)
        time.sleep(wait)

trackCodes = ['2', '7', '13', '3', '22', '48', '47', '27', '43', '59', '75', '56', '112', '99', '103', '145']

if __name__=='__main__':
    dataFile = open(sys.argv[1], 'r').read()
    event = sys.argv[2]
    threads = int(sys.argv[3])
    data = []
    p = re.compile('[0-9]{,3}[.][0-9]{6},[0-9]{,3}[.][0-9]{6},[0-9.]{,8}', re.IGNORECASE)
    for m in p.finditer(dataFile):
        line = m.group(0)
        data.append(line.split(','))
    
    for i in range(threads):
        trackCode = trackCodes[i]
        u = userThread(event, trackCode, data)
        u.start()
