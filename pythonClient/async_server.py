#!/usr/bin/env python
'''
Pymodbus Asynchronous Server Example
--------------------------------------------------------------------------

The asynchronous server is a high performance implementation using the
twisted library as its backend.  This allows it to scale to many thousands
of nodes which can be helpful for testing monitoring software.
'''
#---------------------------------------------------------------------------#
# import the various server implementations
#---------------------------------------------------------------------------#
import sys
from pymodbus.server.async import StartTcpServer
from pymodbus.server.async import StartUdpServer
from pymodbus.server.async import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

#---------------------------------------------------------------------------#
# Multiprocessing imports
#---------------------------------------------------------------------------#
from multiprocessing import Queue, Process

#---------------------------------------------------------------------------#
# Device specific imports
#---------------------------------------------------------------------------#
import RPi.GPIO as RPIO
from SCPV_D import SCPV_D_t
#---------------------------------------------------------------------------#
# configure the service logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# initialize your data store
#---------------------------------------------------------------------------#
# The datastores only respond to the addresses that they are initialized to.
# Therefore, if you initialize a DataBlock to addresses of 0x00 to 0xFF, a
# request to 0x100 will respond with an invalid address exception. This is
# because many devices exhibit this kind of behavior (but not all)::
#
#     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
#
# Continuing, you can choose to use a sequential or a sparse DataBlock in
# your data context.  The difference is that the sequential has no gaps in
# the data while the sparse can. Once again, there are devices that exhibit
# both forms of behavior::
#
#     block = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
#     block = ModbusSequentialDataBlock(0x00, [0]*5)
#
# Alternately, you can use the factory methods to initialize the DataBlocks
# or simply do not pass them to have them initialized to 0x00 on the full
# address range::
#
#     store = ModbusSlaveContext(di = ModbusSequentialDataBlock.create())
#     store = ModbusSlaveContext()
#
# Finally, you are allowed to use the same DataBlock reference for every
# table or you you may use a seperate DataBlock for each table. This depends
# if you would like functions to be able to access and modify the same data
# or not::
#
#     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
#     store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
#
# The server then makes use of a server context that allows the server to
# respond with different slave contexts for different unit ids. By default
# it will return the same context for every unit id supplied (broadcast
# mode). However, this can be overloaded by setting the single flag to False
# and then supplying a dictionary of unit id to context mapping::
#
#     slaves  = {
#         0x01: ModbusSlaveContext(...),
#         0x02: ModbusSlaveContext(...),
#         0x03: ModbusSlaveContext(...),
#     }
#     context = ModbusServerContext(slaves=slaves, single=False)
#
# The slave context can also be initialized in zero_mode which means that a
# request to address(0-7) will map to the address (0-7). The default is
# False which is based on section 4.4 of the specification, so address(0-7)
# will map to (1-8)::
#
#     store = ModbusSlaveContext(..., zero_mode=True)
#---------------------------------------------------------------------------#



#---------------------------------------------------------------------------#
# create your custom data block with callbacks
#---------------------------------------------------------------------------#

class CallbackDataBlock(ModbusSequentialDataBlock):
    ''' A datablock that stores the new value in memory
    and passes the operation to a message queue for further
    processing.
    '''

    def __init__(self, address,values, queue):
        '''
        '''
        self.queue = queue
        super(CallbackDataBlock, self).__init__(address,values)
    def setValues(self, address, values):
        ''' Sets the requested values of the datastore

        :param address: The starting address
        :param values: The new values to be set
        '''
        super(CallbackDataBlock, self).setValues(address, values)
        self.queue.put((address,values))
        log.debug("should have put in queue by now")


#---------------------------------------------------------------------------#
# create the queue that will convey msgs to the controller
#---------------------------------------------------------------------------#
Q = Queue()

store = ModbusSlaveContext(
    di = CallbackDataBlock(0, [17]*100,Q),
    co = CallbackDataBlock(0, [17]*100,Q),
    hr = CallbackDataBlock(0, [17]*100,Q),
    ir = CallbackDataBlock(0, [17]*100,Q))
context = ModbusServerContext(slaves=store, single=True)

#---------------------------------------------------------------------------#
# initialize the server information
#---------------------------------------------------------------------------#
# If you don't set this or any fields, they are defaulted to empty strings.
#---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName  = 'Pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'Pymodbus Server'
identity.ModelName   = 'Pymodbus Server'
identity.MajorMinorRevision = '1.0'

#---------------------------------------------------------------------------#
# run the server you want
#---------------------------------------------------------------------------#
def serverStart(ip,port):
    StartTcpServer(context, identity=identity, address=(ip, port))
#---------------------------------------------------------------------------#
# Function for va;ve controller loop
#---------------------------------------------------------------------------#
def valveControlLoop(queue):
    mController = SCPV_D_t([40,38,36])
    while True:
        address,val = queue.get()
        log.debug('ADDRESS IS: %d',address)
        if address is 0x0f+1:
            log.debug('ADDRESS IS: CORRECT')
            log.debug(val)
            mController.movePosition(val[0])

if __name__ == "__main__":
    RPIO.setmode(RPIO.BOARD)
    log.debug("Creating Process")
    p = Process(target = valveControlLoop, args = (Q,))
    log.debug("Process Created")
    p.start()
    log.debug("Process Started, Starting Server")
    StartTcpServer(context, identity=identity, address=("192.168.1.4",502))
#StartUdpServer(context, identity=identity, address=("localhost", 502))
#StartSerialServer(context, identity=identity, port='/dev/pts/3', framer=ModbusRtuFramer)
#StartSerialServer(context, identity=identity, port='/dev/pts/3', framer=ModbusAsciiFramer)
