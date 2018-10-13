#!/usr/bin/env python

import csv, sys
from datetime import timedelta

def readEvo(fileName, cp, lap):
    data = []
    keys = {}
    with open(fileName, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        lineCnt = 0
        for row in csvreader:
            if lineCnt == 0:
                hI = 0
                for h in row:
                    keys[h] = hI
                    hI = hI + 1
            else:
                entry = {}
                entry['trackCode'] = row[keys['Bib']]
                clocks = []
                clock = row[keys['Clock_Start']]
                if clock != 'n.a.':
                    clocks.append((0, 0, clock))
                for lapI in range(1, lap+1):
                    for cpI in range(1, cp):
                        k = 'Clock_Split%s_Lap%s' % (cpI, lapI)
                        clock = row[keys[k]]
                        if clock != 'n.a.':
                            clocks.append((lapI, cpI, clock))

                    clock = row[keys['Clock_Finish_Lap%s' % (lapI)]]
                    if clock != 'n.a.':
                        clocks.append((lapI, cp, clock))
                entry['clocks'] = clocks
                data.append(entry)
                #print row
            lineCnt = lineCnt + 1
    return data

def evo2sql(entry):
    for c in entry['clocks']:
        print """insert into event_msg_x(event_fk, trackCode, lap, cp, update_time) values ('%s', '%s', '%s', '%s', timestamp '2013-10-19 %s' + interval '4 seconds');""" % (31, entry['trackCode'], c[0], c[1], c[2])

def s2time(s):
    return timedelta(hours=int(s[0:2]), minutes=int(s[3:5]), seconds=int(s[6:8]))

def d2s(d):
    hours, remainder = divmod(d.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%s:%02d:%02d' % (hours, minutes, seconds)

def estimate(entry, segments, laps):
    clocks = entry['clocks']
    newClocks = []
    for l in range(laps):
        for c in range(len(segments)):
            segment = clocks[l*len(segments)+c:l*len(segments)+c+2]
            newClocks.append(segment[0][2])
            tStart = s2time(segment[0][2])
            tEnd = s2time(segment[1][2])
            interval = (tEnd - tStart)/(segments[c] + 1)
            tx = tStart
            for i in range(1, segments[c] + 1):
                tx = tx + interval
                newClocks.append(d2s(tx))
            newClocks.append(segment[1][2])
    entry['eClocks'] = newClocks

def evo2sqlPos(entry, coords, laps):
    clocks = entry['eClocks']
    for l in range(laps):
        for i in range(len(coords)):
            print """insert into position(event_fk, trackCode, lat, lon, alt, gps_time, update_time, estimated) values (31, '%s', %s, %s, 0, '2013-10-19 %s', '2013-10-19 %s', 't');""" % (entry['trackCode'], coords[i][0], coords[i][1], clocks[l * len(coords) + i], clocks[l * len(coords) + i]) 

data = readEvo(sys.argv[1], 5, 7)
#d = data[114]
#print d, len(d['clocks'])

#for d in data:
#    evo2sql(d)

#d = data[1]
#print d

segments = [10, 6, 4, 16, 1]
eCoords = [('44.41205978', '26.10467911'), ('44.41083908', '26.10475922'), ('44.40964890', '26.10485077'), ('44.40864944', '26.10499001'), ('44.40769958', '26.10584068'), ('44.40745163', '26.10709000'), ('44.40662003', '26.10782051'), ('44.40657043', '26.10750961'), ('44.40586853', '26.10869980'), ('44.40483093', '26.10880089'), ('44.40559006', '26.10816002'), ('44.40644836', '26.10849953'), ('44.40644836', '26.10849953'), ('44.40702820', '26.10964966'), ('44.40719986', '26.11091042'), ('44.40702057', '26.11141014'), ('44.40618134', '26.11128044'), ('44.40607071', '26.11027908'), ('44.40533066', '26.10930061'), ('44.40475845', '26.10914993'), ('44.40475845', '26.10914993'), ('44.40401077', '26.10901070'), ('44.40336990', '26.10840988'), ('44.40354156', '26.10777092'), ('44.40367126', '26.10708046'), ('44.40306091', '26.10713959'), ('44.40306091', '26.10713959'), ('44.40261078', '26.10561943'), ('44.40264893', '26.10390091'), ('44.40338898', '26.10250092'), ('44.40438843', '26.10173988'), ('44.40533829', '26.10165024'), ('44.40613937', '26.10242081'), ('44.40700912', '26.10154915'), ('44.40745163', '26.10025978'), ('44.40853119', '26.09951973'), ('44.40956879', '26.10059929'), ('44.41035843', '26.10172081'), ('44.41106033', '26.10327911'), ('44.41143036', '26.10440063'), ('44.41252136', '26.10387039'), ('44.41226959', '26.10250092'), ('44.41276169', '26.10297012'), ('44.41305161', '26.10391045'), ('44.41305161', '26.10391045'), ('44.41313934', '26.10404968'), ('44.41205978', '26.10467911')]

for d in data[:20]:
    if len(d['clocks']) == 5*7+1:
        estimate(d, segments, 7)
        evo2sqlPos(d, eCoords, 7)
