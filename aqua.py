#kopieren mit: sudo cp /media/homebasenas/maschinen/aquapi/aqua.py ~/EigeneScripts/aqua.py


import time
import csv
import pigpio
import math
from random import randint
from numpy import genfromtxt

time.sleep(5.00)


#_______________________________________________________________________________________________________________________	
#CSV
csv = genfromtxt('/home/pi/EigeneScripts/tagesverlauf.csv', delimiter=';')
spalterot = 1
spaltegruen = 2
spalteblau = 3
spalteweiss = 4

#_______________________________________________________________________________________________________________________	
#GPIO Setup und Start

#PWM Frequenz für die LEDs:
frequency = 200

#Pin Belegung
r = 27
g = 22
b = 24
y = 25

#connect to local Pi
pi = pigpio.pi() 

#initialization
pi.set_PWM_frequency(r,frequency)
pi.set_PWM_frequency(g,frequency)
pi.set_PWM_frequency(b,frequency)
pi.set_PWM_frequency(y,frequency)

i = 0
for i in range (0, 255):
    pi.set_PWM_dutycycle(r, i)
    pi.set_PWM_dutycycle(g, i)
    pi.set_PWM_dutycycle(b, i)
    pi.set_PWM_dutycycle(y, i)
    i = i + 1
    time.sleep(0.01)
time.sleep(2.00)

#_______________________________________________________________________________________________________________________	
#Wettereinflüsse

#Wetter:
import pyowm
owm = pyowm.OWM('30536372c28837757532ece34999092b')

def bedeckung (rnach):
    obs = owm.weather_at_place('Berlin,de')
    w = obs.get_weather()
    x = w.get_clouds() 
    print "Bedeckung: ", x
    if rnach == 255:
        wolken = int((math.fabs(x-100))*255/100)
    else:
        wolken = rnach
    return wolken


# wenn Helligkeitswerte für nächste Stunde unterschiedlich, dann enable fading, sonst Wettereinflüsse, nur tagsüber
#Regen, mehr weißgrau
#def wetterregen (rpin,rvor,gpin,gvor,bpin,bvor,ypin,yvor):
#    print "Regen"


#Sonne, mehr gelb, morgens und abends mehr rot
#def wettersonnig (rpin,rvor,gpin,gvor,bpin,bvor,ypin,yvor):
#    print "Sonne"


#Wolken, abwechselnd mehr grau und mehr blau
#def wetterwolkig (rpin,rvor,gpin,gvor,bpin,bvor,ypin,yvor):
#    print "Wolken"
#    x = 100
#    while x>0:
#        if yvor>0 and yvor<255:
#            yvor = yvor -1
#            pi.set_PWM_dutycycle(ypin, yvor)
#            x = x-1
#            time.sleep(0.001)
#    y = 100
#    while y>0:
#        if yvor>0 and yvor<255:
#            yvor = yvor +1
#            pi.set_PWM_dutycycle(ypin, yvor)
#            y = y-1
#            time.sleep(0.001)
#
#def wettervollmond (rpin,rvor,gpin,gvor,bpin,bvor,ypin,yvor):
#    print "Vollmond"
#
#def wetterhalbmond (rpin,rvor,gpin,gvor,bpin,bvor,ypin,yvor):
#    print "Halbmond"

#_______________________________________________________________________________________________________________________	
#Funktionen

def wertermitteln (farbe, csvarray, spalte, pin):
    #Zeit ermitteln
    nowhour = int(time.strftime("%H"))
    nowminute = int(time.strftime("%M"))
    #Werte jetzt und gleich aus CSV lesen
    jetzt = csvarray[nowhour][spalte]
    if nowhour ==23:
        gleich = csvarray[0][spalte]
    else:
        gleich = csvarray[nowhour+1][spalte]
    #Helligkeitswert für jetzige Minute errechnen
    if nowminute == 0:
        hell = gleich
    else:
        hell = int(jetzt + ((gleich - jetzt)/60*nowminute))
    #Werte ausserhalb Range abfangen
    if hell >255:
        hell = 255
    elif hell < 0:
        hell = 0
    return hell

def fading (rpin, rvor, rnach, gpin, gvor, gnach, bpin, bvor, bnach, ypin, yvor, ynach):
    #Betrag: 
    rb = math.fabs(rvor-rnach)
    gb = math.fabs(gvor-gnach)
    bb = math.fabs(bvor-bnach)
    yb = math.fabs(yvor-ynach)
    #Groesster Wert:
    list1 = [rb, gb, bb, yb]
    maximum = max(list1)
    print "-------------Fadingzyklus Start-------------"
    print "Fadingdifferenz:"
    print "Rot: ", rb
    print "Gruen: ", gb
    print "Blau: ", bb
    print "Weiss: ", yb
    print "Maximale Differenz: ", maximum

    while maximum != 0:
        if rvor > rnach:
            rvor = rvor - 1
            print "Rot: ", rvor
            pi.set_PWM_dutycycle(rpin, rvor)
        elif rvor < rnach:
            rvor = rvor + 1
            print "Rot: ", rvor
            pi.set_PWM_dutycycle(rpin, rvor)
        if gvor > gnach:
            gvor = gvor - 1
            print "Gruen: ", gvor
            pi.set_PWM_dutycycle(gpin, gvor)
        elif gvor < gnach:
            gvor = gvor + 1
            print "Gruen: ", gvor
            pi.set_PWM_dutycycle(gpin, gvor)
        if bvor > bnach:
            bvor = bvor - 1
            print "Blau: ", bvor
            pi.set_PWM_dutycycle(bpin, bvor)
        elif bvor < bnach:
            bvor = bvor + 1
            print "Blau: ", bvor
            pi.set_PWM_dutycycle(bpin, bvor)
        if yvor > ynach:
            yvor = yvor - 1
            print "Weiss: ", yvor
            pi.set_PWM_dutycycle(ypin, yvor)
        elif yvor < ynach:
            yvor = yvor + 1
            print "Weiss: ", yvor
            pi.set_PWM_dutycycle(ypin, yvor)
        maximum = maximum - 1
        time.sleep(0.03)
    print "-------------Fadingzyklus Ende-------------"
    return





#_______________________________________________________________________________________________________________________	
#Programm

try:
    while True:
        #Fading
        print "-------------Zyklus Start-------------"
        rvor = pi.get_PWM_dutycycle(r)
        gvor = pi.get_PWM_dutycycle(g)
        bvor = pi.get_PWM_dutycycle(b)
        yvor = pi.get_PWM_dutycycle(y)
        rnach = wertermitteln("Rot", csv, spalterot, r)
        #rnachwolke = bedeckung(rnach)
        gnach = wertermitteln("Gruen", csv, spaltegruen, g)
        bnach = wertermitteln("Blau", csv, spalteblau, b)
        ynach = wertermitteln("Weiss", csv, spalteweiss, y)
        fading(r,rvor,rnach,g,gvor,gnach,b,bvor,bnach,y,yvor,ynach)
        #Warten
        print "-------------Zyklus Ende-------------"
        time.sleep(60.00)
     
#_______________________________________________________________________________________________________________________
#Beenden/Aufräumen			
except KeyboardInterrupt:
    pi.stop()
    print "Beendet"
    pass
