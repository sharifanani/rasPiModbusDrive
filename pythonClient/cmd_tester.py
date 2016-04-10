# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pymodbus.client.sync import ModbusTcpClient
#
# #modbus connection
client = ModbusTcpClient('localhost')
connection = client.connect()
#
# #read register
# client.write_registers(0x000f, [6,7,8])
# request = client.read_holding_registers(0x000f,3) #covert to float
# result = request.registers
# print result
#write to register
#client.write_registers(xxxx, [xxxx,xxxx,xxxx])
while True:
    numInput = input("Enter Desired Position ")
    if numInput<255:
        client.write_register(0x000f,numInput)
        pass
    else:
        print ("Invalid number, number needs to be 0-->255")
    pass
