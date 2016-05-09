#!/usr/bin/python

#Script to push Smartctl metrics to cosmos
#Author: harsharaj.h@flipkart.com

import subprocess
import sys
import os
import time

#Function to get the Serial number and corresponding disk name
def matchDiskSerial():
    cmd="hdparm -I /dev/sd? | grep -B5 Serial\ Number  | grep -v Model| grep -v ATA| xargs -n5 | awk '{print $1, $4}'| tr -d :"
    disk_match = subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    diskmatch =disk_match.stdout.readlines()
    diskDet = []
    for i in diskmatch:
     diskDet.append(i.strip())
    disk_match.terminate()
    return diskDet

#Function to get the Model number
def modelNumber():
    cmd="hdparm -I /dev/sd? | grep -v Serial\ Number  | grep Model| grep -v ATA | awk '{print $NF}'"
    model_number = subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    modelnumber =model_number.stdout.readlines()
    modelNum = [] 
    for i in modelnumber:
     modelNum.append(i.strip())
    model_number.terminate()
    return modelNum	

#Function to get required Smartctl attributes
def diskAttrib(diskname):
    cmd="smartctl -A %s | grep -w 'ID#' -A200| grep -v 'ID#'|awk '{print $1, $2, $9,$10}'| awk NF" %diskname.strip()
    attribs_list = subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    attribs =attribs_list.stdout.readlines()
    attribs_list.terminate()
    return attribs

#Function to get required Smartctl attributes
def diskextAttrib(diskname):
    if "TOSHIBA" in subprocess.check_output("lsscsi | grep %s" % diskname.strip(), shell=True):
        return ""
    cmd="smartctl -x %s |  sed -n '/Page/,/^$/p'| grep -v \"|\" | grep -v ^$|grep -v === | grep -v Page|grep -v -i \"Unknown\"|sed  -r 's/(\s+)?\S+//1' | sed  -r 's/(\s+)?\S+//1' | sed  -r 's/(\s+)?\S+//1' | sed 's/^ *//g' | awk -F \"  \" '{print $1,\" \"$2}' | awk -F     \"  \" '{gsub(/ /,\"_\",$2); print }' |  awk -F \"  \" '{gsub(/~/,\"\",$1); print }'" %diskname.strip()
    attribsext_list = subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    attribsext =attribsext_list.stdout.readlines()
    attribsext_list.terminate()
    return attribsext

#Function to get the hostname
def findHostname():
        cmd="hostname"
        host_addr=subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        hosts=host_addr.stdout.readlines()
        host_addr.terminate()
        hostaddr=hosts[0].strip()
        return hostaddr

attmatch = {'1':'Read_Error_Rate', '2':'Throughput_Performance', '3':'Spin-Up_Time', '4':'Start/Stop_Count', '5':'Reallocated_Sectors_Count', '6':'Read_Channel_Margin', '7':'Seek_Error_Rate', '8':'Seek_Time_Performance', '9':'Power-On_Hours', '10':'Spin_Retry_Count', '11':'Recalibration_Retries', '12':'Power_Cycle_Count', '13':'Soft_Read_Error_Rate', '22':'Current_Helium_Level', '170':'Available_Reserved_Space', '171':'SSD_Program_Fail_Count', '172':'SSD_Erase_Fail_Count', '173':'SSD_Wear_Leveling_Count', '174':'Unexpected_power_loss_count', '175':'Power_Loss_Protection_Failure', '176':'Erase_Fail_Count', '177':'Wear_Range_Delta', '179':'Used_Reserved_Block_Count_Total', '180':'Unused_Reserved_Block_Count_Total', '181':'Program_Fail_Count_Total', '182':'Erase_Fail_Count', '183':'Runtime_Bad_Block', '184':'End-to-End_error', '185':'Head_Stability', '186':'Induced_Op-Vibration_Detection', '187':'Reported_Uncorrectable_Errors', '188':'Command_Timeout', '189':'High_Fly_Writes', '190':'Temperature_Difference_from_100', '190':'Airflow_Temperature', '191':'G-sense_Error_Rate', '192':'Power-off_Retract_Count', '193':'Load_Cycle_Count', '194':'Temperature_resp', '195':'Hardware_ECC_Recovered', '196':'Reallocation_Event_Count', '197':'Current_Pending_Sector_Count', '198':'Uncorrectable_Sector_Count', '199':'UltraDMA_CRC_Error_Count', '200':'Write_Error_Rate', '200':'Multi-Zone_Error_Rate', '201':'Soft_Read_Error_Rate', '202':'Data_Address_Mark_errors', '203':'Run_Out_Cancel', '204':'Soft_ECC_Correction', '205':'Thermal_Asperity_Rate', '206':'Flying_Height', '207':'Spin_High_Current', '208':'Spin_Buzz', '209':'Offline_Seek_Performance', '210':'Vibration_During_Write', '211':'Vibration_During_Write', '212':'Shock_During_Write', '220':'Disk_Shift', '221':'G-Sense_Error_Rate', '222':'Loaded_Hours', '223':'Load/Unload_Retry_Count', '224':'Load_Friction', '225':'Load/Unload_Cycle_Count', '226':'Load_In-time', '227':'Torque_Amplification_Count', '228':'Power-Off_Retract_Cycle', '230':'GMR_Head_Amplitude', '230':'Drive_Life_Protection_Status', '231':'Temperature', '231':'SSD_Life_Left', '232':'Endurance_Remaining', '232':'Available_Reserved_Space', '233':'Power-On_Hours', '233':'Media_Wearout_Indicator', '234':'Average_erase_count_AND_Maximum_Erase_Count', '235':'Good_Block_Count_AND_System_Block_Count', '240':'Transfer_Error_Rate', '240':'Head_Flying_Hours', '241':'Total_LBAs_Written', '242':'Total_LBAs_Read', '243':'Total_LBAs_Written_Expanded', '244':'Total_LBAs_Read_Expanded', '249':'NAND_Writes_1GiB', '250':'Read_Error_Retry_Rate', '251':'Minimum_Spares_Remaining', '252':'Newly_Added_Bad_Flash_Block', '254':'Free_Fall_Protection', '16':'Unknown_Attribute'};


attrs=[ "Read_Error_Rate", "Reallocated_Sectors_Count", "Spin_Retry_Count", "Runtime_Bad_Block", "End-to-End_error", "Reported_Uncorrectable_Errors", "Command_Timeout", "Reallocation_Event_Count", "Current_Pending_Sector_Count", "Uncorrectable_Sector_Count", "Soft_Read_Error_Rate", "Drive_Life_Protection_Status"]


if __name__ == "__main__":
  ticks = int(time.time())
  hostfind=findHostname()
  disklist = []
  disk_match=matchDiskSerial()
  model_number=modelNumber()
  if len(disk_match) == len(model_number):
   for i in range(len(disk_match)):
    tm = str(disk_match[i]) + " " + str(model_number[i])
    disklist.append(tm)
 
  Total_LBAs_Written=0
  Power_On_Hours=0
  Total_LBAs_Read=0
  Logical_Sectors_Read=0
  Logical_Sectors_Written=0
  Power_on_Hours=0
  
  ch = []
  for i in disklist:
    ne = {}
    tmp = {}
    i= i.strip()
    i=i.split()
    diskname=i[0]
    diskModel=i[2]
    serial=i[1]
    attrib=diskAttrib(diskname)
    for j in attrib:
     j=j.strip()
     j=j.split()
     smart_id = j[0]
     val = j[3]
     if smart_id in attmatch.keys():
      atrt = attmatch[smart_id]
      print ticks, "dc.smart.param", val, "host=%s" %hostfind, "diskName=%s" %diskname, "attrName=%s" %atrt, "serialName=%s" %serial, "diskModel=%s" %diskModel
     if atrt == 'Power-On_Hours':
        Power_On_Hours = j[3]
     if atrt == 'Total_LBAs_Written':
        Total_LBAs_Written = j[3]
     if atrt == 'Total_LBAs_Read':
        Total_LBAs_Read = j[3] 
  
     if atrt in attrs:
       if int(val) >  0:
        if atrt in tmp:
         tmp[atrt] = tmp[atrt] + 1
        else:
         tmp[atrt] = 1
    ne[diskModel] = tmp
    ch.append(ne)
  nwdic = {}
  for i in ch:
   for j in i:
    if len (i[j].keys()) > 0:
     if j not in nwdic:
      tmp = {}
      for k in i[j].keys():
       if k not in tmp:
        tmp[k] = 1
       else:
        tmp[k] = tmp[k] + 1
      nwdic[j] = tmp
     else:
      for l in i[j].keys():
       if l in nwdic[j]:
        nwdic[j][l] = nwdic[j][l] + 1
       else:
        nwdic[j][l] = 1
    attribext=diskextAttrib(diskname)
    for k in attribext:
     k=k.strip()
     k=k.split()
     rw_value=k[0]
     atrtext=k[1]
     if atrtext == 'Power-on_Hours':
        Power_on_Hours = k[0]
     if atrtext == 'Logical_Sectors_Read':
        Logical_Sectors_Read = k[0]
     if atrtext == 'Logical_Sectors_Written':
        Logical_Sectors_Written = k[0]

     print ticks, "dc.smart.param", rw_value, "host=%s" %hostfind, "diskName=%s" %diskname, "attrName=%s" %atrtext, "serialName=%s" %serial, "diskModel=%s" %diskModel
    
   year=float(Power_On_Hours)/(24*365)
   space= ((float(Total_LBAs_Read)*65536*512)+(float(Total_LBAs_Written)*65536*512))/(2*1024*1024*1024*1024)
   spyr= float(space)/float(year)
   yearext=float(Power_on_Hours)/(24*365)
   spyrext=0
   if float(yearext) != 0.0:
     spaceext=((float(Logical_Sectors_Written)*512)+(float(Logical_Sectors_Read)*512))/(2*1024*1024*1024*1024)
     spyrext= spaceext/yearext

  for i in nwdic:
   for j in nwdic[i]:
    print ticks, "dc.smart.param", nwdic[i][j], "host=%s" %hostfind, "attrName=%s" %j, "diskModel=%s" %i
    
   
