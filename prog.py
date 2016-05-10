#!/usr/bin/python

#Script to push Smartctl metrics to cosmos
#Author: harsharaj.h@flipkart.com

import subprocess
import sys
import os
import time
from func import *

if __name__ == "__main__":
    time_ticks = int(time.time())
    host_find=find_hostname()
    disk_list=[]
    disk_match=match_diskserial()
    model_number=model_number()
    if len(disk_match) == len(model_number):
        for index in range(len(disk_match)):
            new_list = str(disk_match[index]) + " " + str(model_number[index])
            disk_list.append(new_list)
 
    total_lbas_written=0
    power_on_hours=0
    total_lbas_read=0
    logical_sectors_read=0
    logical_sectors_written=0
    power_on_hours_ext=0
  
    counter_list=[]
    for disk in disk_list:
        ne = {}
        tmp = {}
        disk=disk.strip()
        disk=disk.split()
        disk_name=disk[0]
        disk_model=disk[2]
        serial_number=disk[1]
        attribute_list=disk_attrib(disk_name)
        for attribute in attribute_list:
            attribute=attribute.strip()
            attribute=attribute.split()
            smart_id = attribute[0]
            raw_val = attribute[3]
            if smart_id in att_match.keys():
                atrt = att_match[smart_id]
                print time_ticks, "dc.smart.param", raw_val, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=%s" %atrt, "serialName=%s" %serial_number, "diskModel=%s" %disk_model
            if atrt == 'Power-On_Hours':
                power_on_hours = attribute[3]
            if atrt == 'Total_LBAs_Written':
                total_lbas_written = attribute[3]
            if atrt == 'Total_LBAs_Read':
                total_lbas_read = attribute[3] 
  
            if atrt in attr_check:
                if int(raw_val) >  0:
                    if atrt in tmp:
                        tmp[atrt] = tmp[atrt] + 1
                    else:
                        tmp[atrt] = 1
        ne[disk_model] = tmp
        counter_list.append(ne)
        attrib_ext=diskext_attrib(disk_name)
        #print attrib_ext
        for ext_attrib in attrib_ext:
            ext_attrib=ext_attrib.strip()
            ext_attrib=ext_attrib.split()
            rw_value=ext_attrib[0]
            atrt_ext=ext_attrib[1]
            if atrt_ext == 'Power-on_Hours':
                power_on_hours_ext = ext_attrib[0]
            if atrt_ext == 'Logical_Sectors_Read':
                logical_sectors_read = ext_attrib[0]
            if atrt_ext == 'Logical_Sectors_Written':
                logical_sectors_written = ext_attrib[0]

                print time_ticks, "dc.smart.param", rw_value, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=%s" %atrt_ext, "serialName=%s" %serial_number, "diskModel=%s" %disk_model
            
        year=float(power_on_hours)/(24*365)
        space= ((float(total_lbas_read)*65536*512)+(float(total_lbas_written)*65536*512))/(2*1024*1024*1024*1024)
        spyr= float(space)/float(year)
            
        yearext=float(power_on_hours_ext)/(24*365)
        if float(yearext) != 0.0:
            spaceext=((float(logical_sectors_written)*512)+(float(logical_sectors_read)*512))/(2*1024*1024*1024*1024)
            spyrext= spaceext/yearext
        if float(spyr) !=0:
            if float(spyr) > 0 and float(spyr) <= 200:
                print time_ticks, "dc.smart.param", spyr, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc200", "diskModel=%s" %disk_model       
            if float(spyr) > 200 and float(spyr) <= 400:
                print time_ticks, "dc.smart.param", spyr, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc400", "diskModel=%s" %disk_model  
            if float(spyr) > 400 and float(spyr) <= 600:
                print time_ticks, "dc.smart.param", spyr, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc600", "diskModel=%s" %disk_model
            if float(spyr) > 600 :
                print time_ticks, "dc.smart.param", spyr, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc", "diskModel=%s" %disk_model

        elif float(spyrext)!=0:
            if float(spyrext) > 0 and float(spyrext) <= 200:
                print time_ticks, "dc.smart.param", spyrext, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc200", "diskModel=%s" %disk_model      
            if float(spyrext) > 200 and float(spyrext) <= 400:
                print time_ticks, "dc.smart.param", spyrext, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc400", "diskModel=%s" %disk_model   
            if float(spyrext) > 400 and float(spyrext) <= 600:
                print time_ticks, "dc.smart.param", spyrext, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc600", "diskModel=%s" %disk_model
            if float(spyrext) > 600 :
                print time_ticks, "dc.smart.param", spyrext, "host=%s" %host_find, "diskName=%s" %disk_name, "attrName=lbcalc", "diskModel=%s" %disk_model



    counter_dict={}
    for disk_mod_dict in counter_list:
        for disk_mod in disk_mod_dict:
            if len (disk_mod_dict[disk_mod].keys()) > 0:
                if disk_mod not in counter_dict:
                    tmp = {}
                    for att_count in disk_mod_dict[disk_mod].keys():
                        if att_count not in tmp:
                            tmp[att_count] = 1
                        else:
                            tmp[att_count] = tmp[att_count] + 1
                    counter_dict[disk_mod] = tmp
                else:
                    for attrib_count in disk_mod_dict[disk_mod].keys():
                        if attrib_count in counter_dict[disk_mod]:
                            counter_dict[disk_mod][attrib_count] = counter_dict[disk_mod][attrib_count] + 1
                        else:
                            counter_dict[disk_mod][attrib_count] = 1
            
        
            
        
    for disk_model in counter_dict:
        for attr_name in counter_dict[disk_model]:
            print time_ticks, "dc.smart.param", counter_dict[disk_model][attr_name], "host=%s" %host_find, "attrName=%s" %attr_name, "diskModel=%s" %disk_model
