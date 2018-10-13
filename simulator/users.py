#!/usr/bin/env python
import csv, sys

with open(sys.argv[1], 'rb') as csvfile:
    userreader = csv.reader(csvfile, delimiter=',', quotechar='\'')
    firstRow = True
    sel1 = 'insert into event_user ('
    sel2 = ') values ('
    for row in userreader:
        if firstRow:
            for cName in row:
                sel1 = sel1 + cName + ', '
                if cName <> 'event_fk':
                    sel2 = sel2 + """'%s', """
                else:
                    sel2 = sel2 + """%s, '"""
            sel1 = sel1[:-2] + sel2[:-3] + ');'
            firstRow = False
        else:
            print (sel1 % tuple(row)).replace('\'\'', 'null')
