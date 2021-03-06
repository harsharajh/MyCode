#!/usr/bin/python

from urllib import urlopen
from json import loads
import datetime
import time 

attrs=[ "Read_Error_Rate", "Reallocated_Sectors_Count", "Spin_Retry_Count", "Runtime_Bad_Block", "End-to-End_error", "Reported_Uncorrectable_Errors", "Command_Timeout", "Reallocation_Event_Count", "Current_Pending_Sector_Count", "Uncorrectable_Sector_Count", "Soft_Read_Error_Rate", "Drive_Life_Protection_Status"]

attr=["Reallocated_Sectors_Count"]
fle = open("fk-smart-analysis.log", "a")
for att in attrs:
 try:
  url = "http://10.47.2.91/api/query?start=12h-ago&m=sum:fk-cloud.dc.smart.param{attrName=%s,host=*,serialName=*,diskModel=*}" %att
  dat=loads(urlopen(url).read())
  #fle = open("fk-smart-analysis.log", "a")
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
      if tmp[0] > float(0):
       wri = "dc.smart.analysis" + " " + str(att) + " " + str(datetime.datetime.now()) + " " + str(j['tags']['host']) + " " + str( j['tags']['serialName']) + " " + str( j['tags']['diskModel']) +" " + str( j['dps'].values()[0]) + "\n"
       fle.write(wri)
       count += 1
   fi[i] = count

  ticks=int(time.time())
  for i in fi.keys():
   print ticks, "dc.smart.analysis", fi[i], "attrName=%s" %att, "diskModel=%s" %i

#fle.close()
 
 except:
  continue

fle.close()
