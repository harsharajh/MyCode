#!/usr/bin/python

#Script to push Smartctl metrics to cosmos
#Author: harsharaj.h@flipkart.com

import subprocess
import sys
import os
import time

#Function to get the Serial number and corresponding disk name
def match_diskserial():
    cmd="hdparm -I /dev/sd? | grep -B5 Serial\ Number  | grep -v Model| grep -v ATA| xargs -n5 | awk '{print $1, $4}'| tr -d :"
    disk_serial=subprocess.Popen(cmd, shell=True, bufsize=4096, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    disk_match=disk_serial.stdout.readlines()
    disk_det=[]
    for i in disk_match:
        disk_det.append(i.strip())
    disk_serial.terminate()
    return disk_det

#Function to get the Model number
def model_number():
    cmd="hdparm -I /dev/sd? | grep -v Serial\ Number  | grep Model| grep -v ATA | awk '{print $NF}'"
    model_num=subprocess.Popen(cmd, shell=True, bufsize=4096, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    model_numb=model_num.stdout.readlines()
    model_number=[] 
    for i in model_numb:
        model_number.append(i.strip())
    model_num.terminate()
    return model_number	

#Function to get required Smartctl attributes
def disk_attrib(diskname):
    cmd="smartctl -A %s | grep -w 'ID#' -A200| grep -v 'ID#'|awk '{print $1, $2, $9,$10}'| awk NF" %diskname.strip()
    attribs_list=subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    attribs=attribs_list.stdout.readlines()
    attribs_list.terminate()
    return attribs

#Function to get extended Smartctl attributes
def diskext_attrib(diskname):
    if "TOSHIBA" in subprocess.check_output("lsscsi | grep %s" % diskname.strip(), shell=True):
        return ""
    cmd="smartctl -x %s | sed -n '/Page/,/^$/p' | grep -v -e == -e Unknown -e normalized -e ^$ -e Page| awk '{ for(i=4; i<NF; i++) printf $i OFS; if(NF) printf $NF; printf ORS}'" %diskname.strip()
    attribext_list=subprocess.Popen(cmd, shell=True, bufsize=8192, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    attribext_temp=attribext_list.stdout.readlines()
    data=str()
    attrib_ext = []
    for raw_data in attribext_temp:
        counter = 0
        data=''
        for word in raw_data.split(" "):
            if counter == 0:
                data+=word
            elif counter == 1:
                data=data+" "+word
            else:
                data=data+"_"+word
            counter+=1
        attrib_ext.append(data)
    attribext_list.terminate()
    return attrib_ext

#Function to get the hostname
def find_hostname():
    cmd="hostname"
    host_addr=subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    hosts=host_addr.stdout.readlines()
    host_addr.terminate()
    host_address=hosts[0].strip()
    return host_address

att_match = {'1':'Read_Error_Rate', '2':'Throughput_Performance', '3':'Spin-Up_Time', '4':'Start/Stop_Count', '5':'Reallocated_Sectors_Count', '6':'Read_Channel_Margin', 
'7':'Seek_Error_Rate', '8':'Seek_Time_Performance', '9':'Power-On_Hours', '10':'Spin_Retry_Count', '11':'Recalibration_Retries', '12':'Power_Cycle_Count', 
'13':'Soft_Read_Error_Rate', '22':'Current_Helium_Level', '170':'Available_Reserved_Space', '171':'SSD_Program_Fail_Count', '172':'SSD_Erase_Fail_Count', 
'173':'SSD_Wear_Leveling_Count', '174':'Unexpected_power_loss_count', '175':'Power_Loss_Protection_Failure', '176':'Erase_Fail_Count', '177':'Wear_Range_Delta', 
'179':'Used_Reserved_Block_Count_Total', '180':'Unused_Reserved_Block_Count_Total', '181':'Program_Fail_Count_Total', '182':'Erase_Fail_Count', '183':'Runtime_Bad_Block', 
'184':'End-to-End_error', '185':'Head_Stability', '186':'Induced_Op-Vibration_Detection', '187':'Reported_Uncorrectable_Errors', '188':'Command_Timeout', '189':'High_Fly_Writes', 
'190':'Temperature_Difference_from_100', '190':'Airflow_Temperature', '191':'G-sense_Error_Rate', '192':'Power-off_Retract_Count', '193':'Load_Cycle_Count', 
'194':'Temperature_resp', '195':'Hardware_ECC_Recovered', '196':'Reallocation_Event_Count', '197':'Current_Pending_Sector_Count', '198':'Uncorrectable_Sector_Count', 
'199':'UltraDMA_CRC_Error_Count', '200':'Write_Error_Rate', '200':'Multi-Zone_Error_Rate', '201':'Soft_Read_Error_Rate', '202':'Data_Address_Mark_errors', '203':'Run_Out_Cancel', 
'204':'Soft_ECC_Correction', '205':'Thermal_Asperity_Rate', '206':'Flying_Height', '207':'Spin_High_Current', '208':'Spin_Buzz', '209':'Offline_Seek_Performance', 
'210':'Vibration_During_Write', '211':'Vibration_During_Write', '212':'Shock_During_Write', '220':'Disk_Shift', '221':'G-Sense_Error_Rate', '222':'Loaded_Hours', 
'223':'Load/Unload_Retry_Count', '224':'Load_Friction', '225':'Load/Unload_Cycle_Count', '226':'Load_In-time', '227':'Torque_Amplification_Count', '228':'Power-Off_Retract_Cycle', 
'230':'GMR_Head_Amplitude', '230':'Drive_Life_Protection_Status', '231':'Temperature', '231':'SSD_Life_Left', '232':'Endurance_Remaining', '232':'Available_Reserved_Space', 
'233':'Power-On_Hours', '233':'Media_Wearout_Indicator', '234':'Average_erase_count_AND_Maximum_Erase_Count', '235':'Good_Block_Count_AND_System_Block_Count', 
'240':'Transfer_Error_Rate', '240':'Head_Flying_Hours', '241':'Total_LBAs_Written', '242':'Total_LBAs_Read', '243':'Total_LBAs_Written_Expanded', '244':'Total_LBAs_Read_Expanded', 
'249':'NAND_Writes_1GiB', '250':'Read_Error_Retry_Rate', '251':'Minimum_Spares_Remaining', '252':'Newly_Added_Bad_Flash_Block', '254':'Free_Fall_Protection', 
'16':'Unknown_Attribute'};


attr_check=[ "Read_Error_Rate", "Reallocated_:q!Sectors_Count", "Spin_Retry_Count", "Runtime_Bad_Block", "End-to-End_error", "Reported_Uncorrectable_Errors", "Command_Timeout", "Reallocation_Event_Count", "Current_Pending_Sector_Count", "Uncorrectable_Sector_Count", "Soft_Read_Error_Rate", "Drive_Life_Protection_Status"]


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
    
print att_match.keys()
