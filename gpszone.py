#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as XML
import re
import serial
import os
from queue import Queue
from threading import Thread
import math
from time import sleep
import RPi.GPIO as GPIO

serialqueue = Queue(maxsize=0)
servicequeue = Queue(maxsize=0)

greenled = 20
orangeled = 12
button = 27
relay = 18
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(greenled, GPIO.OUT) 
GPIO.setup(orangeled, GPIO.OUT)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(relay, GPIO.OUT)

def handle_KML():
    area = []
    xmlns = ''
    n = 0
    for kmlfile in os.listdir("/boot/RUTER/"):
        if(kmlfile.endswith(".kml")):
            e = XML.parse("/boot/RUTER/" + kmlfile)
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
                        x = float(c.split(',')[0])
                        y = float(c.split(',')[1])
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

def ggatodd(gga):
    l = gga.split(',')
    y = float(l[2])
    ydir = l[3]
    x = float(l[4])
    xdir = l[5]
    yd = math.floor(y/100)
    xd = math.floor(x/100)
    ym = (((y/100) - yd)*100)/60
    xm = (((x/100) - xd)*100)/60
    x = xd+xm
    y = yd+ym
    if(ydir == 'S'):
        y = -y
    if(xdir == 'W'):
        x = -x
    print(x,y)
    return(x,y)

def serialhandle():
    ser = serial.Serial("/dev/ttyUSB0", 4800)
    while(True):
        while not servicequeue.empty():
            if serialqueue.get() == "stopserial":
                break
        line = ser.readline()
        line = line.decode("ISO-8859-1")
        if(re.match("^.GPGGA", line)):
            serialqueue.put(ggatodd(line))
            GPIO.output(greenled, GPIO.LOW)
            sleep(.1)
            GPIO.output(greenled, GPIO. HIGH)
        sleep(.2)

def main():
    area = handle_KML()
    x = 0
    y = 0
    GPIO.output(greenled, GPIO.HIGH)
    while(True):
        inside = False
        while not serialqueue.empty():
            x,y = serialqueue.get()
        for l in area:
            if(point_inside_polygon(x,y,l)):
                inside = True
        if inside:
            GPIO.output(orangeled, GPIO.HIGH)
            GPIO.output(relay, GPIO.HIGH)
            #print("INNE")
        else:
            GPIO.output(orangeled, GPIO.LOW)
            GPIO.output(relay, GPIO.LOW)
            #print("UTE")
        #print(x,y)
        sleep(.1)



mainthread = Thread(target=main)
serialthread = Thread(target=serialhandle)
serialthread.setDaemon(True)
mainthread.start()
serialthread.start()

