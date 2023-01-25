# -*- coding: utf-8 -*-
"""
Created on Fri May 20 14:18:28 2022

@author: Alonso Moran
"""

#Import libraries 
import time 
import asyncio
import struct
import numpy as np
import pandas as pd
import array as arr
import math
from bleak import BleakScanner 
from bleak import BleakClient
from bleak import BleakError
import nest_asyncio
nest_asyncio.apply()

#Identify LuDi devices around and print the address
async def main1():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)      
#asyncio.run(main1()) #set a break point here and read ludi address

#Write device address
# addr  = "E9:9F:6E:84:46:19" # add a breakpoint and add ludi address 
# read_characteristic = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
# write_characteristic = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
# time = 0;

data_array = []
final_data = []
#data_array_hex = []
#Function for data reading after connection //difficult to cast data that has different bytelengths
def notification_handler(sender, data):
    print(f"sender: {data}")
    data_2=list(data)
    print("data equals:", data_2)
    #data_3 = data_2[0:8]
    #data_bytes=bytes(data_3)
    #final = struct.unpack('Q', data_bytes)
    #data_hex=hex(data_2)
    data_array.append(data_2)
    print("array is:", data_array)
    #final_data.append(final)
    
    # for i in data_array:
    #     data_hex = hex(data_array[i])
    #     data_array_hex.append(data_hex)
Pressure_value_array = [] 
#final_pressure = [] #provisional and could delete 
# final_time=0
Time_pressure_array = [[],[],[],[]]
#Time_pressure_array = [[]]*17
#Function for data reading for sensor commands 
def notification_handler2(sender, data):
     print(f"{sender}: {data}")
     data_sensors = list(data)
     Time = data_sensors[0:4]
     mouthpiece = data_sensors[5:6]
     Co2 = data_sensors[7:11]
     Pressure = data_sensors[37:41]
     #Pressure = ' '.join([str(elem) for elem in Pressure])
     Time_bytes = bytes(Time)
     print("time_bytes are:", Time_bytes)
     mouth_bytes = bytes(mouthpiece)
     Co2_bytes = bytes(Co2)
     Pressure_bytes = bytes(Pressure)
     [final_time] = struct.unpack('I', Time_bytes)
     #print("final_time is:",final_time)
     [final_Co2] = struct.unpack('i', Co2_bytes)
     [final_mouth] = struct.unpack('B',mouth_bytes)
     [final_pressure] = struct.unpack('f', Pressure_bytes)
     #[final_pressure[0]] = final_pressure[1] #because first value always 0
     #Pressure_value_array = np.append(final_time,final_pressure,axis=0)
     Time_pressure_array[0].append(final_time)
     Time_pressure_array[1].append(final_mouth)
     Time_pressure_array[2].append(final_Co2)
     Time_pressure_array[3].append(final_pressure)
     
     #print("data equals to:",data_sensors)
     #print(Time_pressure_array)
     #Pressure_value_array.append(final_pressure)
     #data_array.append(data2)  
     

#Write command and convert to ascii
# command = ["3b30", "3c30"]
# command_list = []
def prepare_command(command, command_list):
    for i in range(len(command)):
        output_list = bytearray.fromhex(command[i]).decode()
        output_list_split = output_list.split()
        command_final = bytearray(''.join(output_list_split), encoding = 'utf8')
        command_list.append(command_final)


#Make connection with device and send command
async def main2(addr):
    print("Connecting to device...")
    async with BleakClient(addr) as client:
        print("Connected")
        await client.start_notify(read_characteristic, notification_handler)#allow notification
        for i in range(len(command_list)):
            await client.write_gatt_char(write_characteristic, command_list[i])#write command
        # timeout_start = time.time()
        # while time.time() < timeout_start + timeout: #timer for taking data during x seconds  
        #   pass
            await client.read_gatt_char(read_characteristic)#read obatined data
        # await client.stop_notify(read_characteristic)#stop notification
        # await client.write_gatt_char(write_characteristic, inicio) #send stream stop command
        
#asyncio.run(main2(addr))

#Make connection with device and send sensor commands
async def main3(addr):
    print("Connecting to device...")
    async with BleakClient(addr) as client:
        print("Connected")
        await client.start_notify(read_characteristic, notification_handler2)#allow notification
        #for i in range(len(command_list)):
        await client.write_gatt_char(write_characteristic, command_list[0])#write command
        timeout_start = time.time()
        while time.time() < timeout_start + timeout: #timer for taking data during x seconds  
          pass
        await client.read_gatt_char(read_characteristic)#read obatined data
        await client.stop_notify(read_characteristic)#stop notification
        await client.write_gatt_char(write_characteristic, command_list[1]) #send stream stop command
        
#asyncio.run(main3(addr))


evaluation = []
def compare(data, comp_list):
     for i in range(len(data)):
         if data[i]==comp_list[i]:
             evaluation.append(1)
         else:
             evaluation.append(0)
     print("Evaluation matrix is:", evaluation)       
     


def compare2(data, startend):
    for i in range(len(data)):
             #print (i) 
             row = data[i]
             start = startend[i][0] 
             end = startend[i][1]
             
             for x in range(len(row)): 
                 if row[0] == 0:
                     row[0] = row[1]
                 else:
                     pass
                     
                 if ((row[x] >= start) and (row[x] <= end)):
                     test[i].append(1)
                 else: 
                     test[i].append(0)
                     
    #IF ALL THE VALUES EQUAL TO ONE, THEN PRESSURE TRUE OR SOMETHING LIKE THAT; CASE NOT TO FALSE BUT GIVING THE ERRORS
             
             if all(test[i]): #all the elements are true/1, then print true, else print false 
                sensor_matrix.append(True)
             else:
                sensor_matrix.append(False)
                
             file_eva = open ('evaluation.txt', 'a', newline = '\n') 
             lines = [index[i], ',', str(sensor_matrix[i]), '\n']
             for item in lines:
                 file_eva.write(item)
                 
    file_eva.write('\n')
    file_eva.close()
    
    
    

if  __name__ == "__main__":
    
#   for i in range(len(command_list)):
#       asyncio.run(main(addr, command_list[i]))
      #main(addr, command_list[i])
    #Identify Ludi devices around and print the address     
    asyncio.run(main1())  
    
    #Write device address
    addr  = "EA:B8:AE:BB:7C:92" #ZWEI
    #"E9:9F:6E:84:46:19" #DREI
    #"CF:34:4E:3D:D9:64" #FUENF
    #"CF:34:4E:3D:D9:64" #EINS # add a breakpoint and add ludi address 
    read_characteristic = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
    write_characteristic = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    
    
    #Support commands
    #Write command and convert it to ascii  
    #Support commands
    #command = ["3b30", "3c30"]
    #prepare_command(command, command_list)
    #Make connection with device and send command
    #Support commands
    #asyncio.run(main2(addr))
    #Compare results with comparison list
    #Compare support commands
    #compare_list = [[48, 46, 49, 46, 52, 10, 13, 165, 165, 165, 165],[0, 0, 0, 0, 0, 0, 0, 0, 165, 165, 165, 165]]
    #compare(data_array, compare_list)
    
    #Write command and convert it to ascii 
    #Sensor commands
    command = ["7230","7330"]
    timeout = 10
    
    command_list = [] #??? put it up before the value
    prepare_command(command, command_list)
    
    #Make connection with device and send command
    #Sensor commands
    asyncio.run(main3(addr))
    
    #Comparison matrix
    sensor_matrix = []
    index = ['time', 'mouthpiece','co2_0', 'pressure_0']
    #index = ['time','mouthpiece','co2_0','co2_1','co2_2','co2_3','o2','no2','pressure_0','temperature_0','humidity_0', 'pressure_1','temperature_1','humidity_1','pressure_2','temperature_2','humidity_2','battery']
    startend= [[0,math.inf],[0, 1.5], [1000000, 1100000], [986,995]] #dont need to be accurate ranges, only make sense, i.e. 1080 for forced exhalation
    test = [[],[],[],[]]    
    
    compare2(Time_pressure_array, startend)
    
    