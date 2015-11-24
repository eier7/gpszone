#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as XML
import re
import os
from queue import Queue
from threading import Thread

serialqueue = Queue(maxsize=0)

def handle_KML():
    area = []
    xmlns = ''
    n = 0
    for kmlfile in os.listdir("."):
        if(kmlfile.endswith(".kml")):
            e = XML.parse(kmlfile)
            root = e.getroot()
            for i in root.iter():
                m = re.match(".*({.*}).*", str(i))
                if m:
                    xmlns = m.group(1)
                    break
            for coord in root.iter(xmlns + 'coordinates'):
                area.append([])
                for c in coord.text.split(' '):
                    c = c.replace('\t', '')
                    c = c.replace('\n', '')
                    if(re.match('\d+\..*,\d+\..*', c)):
                        x = c.split(',')[0]
                        y = c.split(',')[1]
                        area[n].insert(n, [x,y])
                n = n + 1
    return area

def point_inside_polygon(x,y,poly):
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

def serialhandle():
    import serial
    ser = serial.Serial("com6", 4800)
    while(True):
        line = ser.readline()
        if(re.match("^$GPGGA")):
            print(line)

Thread(serialhandle())
area = handle_KML()
while(True):
    for l in area:
        print(l)
