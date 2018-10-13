#!/usr/bin/env python

import cgi
import cgitb
cgitb.enable()
#cgitb.enable(display=0, logdir="/tmp/")
from string import Template
from os import system, remove
import re

def generatePin(code, fgcolor, bgcolor):
    oFileName = '/home/len/free/mobile/trackMe/web/pins/pin-%s-%s-%s' % (code, fgcolor, bgcolor)
    tFileName = '/home/len/free/mobile/trackMe/web/pins/base-pin.svg'
    tString = open(tFileName, 'r').read()
    t = Template(tString)
    oFile = open(oFileName + '.svg', 'w')
    oFile.write(t.substitute(code=code, fgcolor=fgcolor, bgcolor=bgcolor))
    oFile.close()
    system('convert -background none -scale 32x32 %s.svg %s.png' % (oFileName, oFileName))
    print open(oFileName + '.png', 'r').read()
    remove(oFileName + '.png')
    remove(oFileName + '.svg')

def getColor(color, defColor):
    if color[0] == '#':
        color = color[1:]
    color = color.upper()
    if not re.match('^[0-9ABCDEF]{6}$', color):
        color = defColor
    return color

form = cgi.FieldStorage()
code = form.getvalue('code', '1')
if not re.match('^[0-9a-zA-Z]{1,4}$', code):
    code = '1'
fgcolor = form.getvalue('fgcolor', '000000')
fgcolor = getColor(fgcolor, '000000')

bgcolor = form.getvalue('color', 'FFFFFF')
bgcolor = getColor(bgcolor, 'FFFFFF')

print "Content-type: image/png"
print

print generatePin(code, fgcolor, bgcolor)
