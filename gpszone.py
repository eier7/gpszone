#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as XML
import re

poly = [ \
    [68.800654, 16.576373], \
    [68.809768, 16.562307], \
    [68.816986, 16.590603], \
    [68.817223, 16.647194], \
    [68.804857, 16.699206], \
    [68.796391, 16.671728], \
    [68.804738, 16.637708], \
    [68.805034, 16.602870]  \
]
def handle_KML():
    e = XML.parse('testrute.kml')
    root = e.getroot()
    for i in root.iter():
        m = re.match(".*({.*}).*", str(i))
        if m:
            xmlns = m.group(1)
            break
    for coord in root.iter(xmlns + 'coordinates'):
        for c in coord.text.split(' '):
            c = c.replace('\t', '')
            print(c)
            print("HEHE")
            x = c.split(',')[0]
            y = c.split(',')[0]
            print(x)

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

def sjekkp(x,y,poly):
    if(point_inside_polygon(x,y,poly)):
        print(x,y,"INNE")
    else:
        print(x,y,"UTE")

sjekkp(68.802963, 16.633619,poly)
sjekkp(68.797516, 16.671237,poly)
sjekkp(68.816340, 16.591314,poly)
sjekkp(68.813265, 16.163565,poly)
handle_KML()
