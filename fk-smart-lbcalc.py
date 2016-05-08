#!/usr/bin/python

from urllib import urlopen
from json import loads
import datetime
import time 


fle = open("fk-smart-analysis.log", "a")
try:
  url = "http://10.47.2.91/api/query?start=12h-ago&m=sum:fk-cloud.dc.smart.param{attrName=lbcalc,host=*,serialName=*,diskModel=*}"
  dat=loads(urlopen(url).read())
  uniqDisk = []
  for i in dat:
   if i['tags']['diskModel'] not in uniqDisk:
    uniqDisk.append(i['tags']['diskModel'])
   fi = {}
  for i in uniqDisk:
   count =0
   for j in dat:
    if j['tags']['diskModel'] == i:
     tmp = sorted(j['dps'].values())
     if len(tmp) > 0:
      if tmp[0] > float(180):
       wri = "dc.smart.analysis" + " " + "lbcalc" + " " + str(datetime.datetime.now()) + " " + str(j['tags']['host']) + " " + str( j['tags']['serialName']) + " " + str( j['tags']['diskModel']) +" " + str( j['dps'].values()[0]) + "\n"
       fle.write(wri)
       count += 1
   fi[i] = count

  ticks=int(time.time())
  for i in fi.keys():
   print ticks, "dc.smart.analysis", fi[i], "attrName=lbcalc", "diskModel=%s" %i

except:
   ticks=int(time.time())
   print ticks, "dc.smart.analysis", 0 , "attrName=lbcalc", "diskModel=NODATA"

fle.close()
