import serial
from threading import Thread
import logging
import can

class crawler():
    def __init__( self , config):
        self.status = {"yaw":90,"pitch":90}
        self.hooks = [] #list of hooks to call when new data is available

	#serial port
        #self.serial = serial.Serial( config.get( "serial", "port"), config.getint( "serial", "baudRate"))
        #self.serialBuffer = b''

	#CANbu
        self.bus = can.ThreadSafeBus(interface='socketcan', channel='can0', bitrate=500000)
        self.incoming = {0x30:"a"}
        self.outgoing = {"accelerator": 0, "steering": 1, "pitch":2, "yaw":3}

        #thread seutp
        self.run = True
        self.mainThread = Thread(target=self.CANMonitor)
        self.mainThread.start()

    def CANMonitor(self):
        while self.run:
            msg = self.bus.recv()

            if msg.arbitration_id not in self.incoming:
                print(f"invalid arbitration 0x{msg.arbitration_id:02x}")
                continue

            newData = { self.incoming[msg.arbitration_id] : int(list(msg.data)[0]) }
            self.syncStatus(newData)

    def setCAN(self, values):
        for key, value in values.items():
            if key not in self.outgoing:
                print(f"invalid key {key}")
                continue

            msg  = can.Message(value)
            msg.arbitration_id = self.outgoing[key]
            self.bus.send(msg)

    def serialMonitor(self):
        #if self.serial.in_waiting:
        while self.run:
            try:
                self.serialBuffer += self.serial.read(max(1,self.serial.in_waiting))
            except serial.serialutil.SerialException as E:
                logging.error(E)
                continue

            if self.serialBuffer:
                #separate completed rows
                packets = self.serialBuffer.split(b'\r\n')[:-1]
                self.serialBuffer = self.serialBuffer.split(b'\r\n')[-1]

                #check for completed rows
                if packets:

                    #update completed rows
                    newData = {}
                    for line in packets:
                        try:
                            var, value = line.decode('utf-8').split(' ')
                            newData.update({var:value})
                        except ValueError:
                            #error in serial data
                            continue

                    #update everyone interested
                    self.syncStatus(newData)

    def syncStatus(self, newData):
        self.status.update(newData)
        for hook in self.hooks:
            hook(newData)

    def addHook(self, hook):
        self.hooks.append(hook)

    def stop(self):
        self.run = False
        self.mainThread.join()

    def set(self, values):
        for key, value in values.items():
            if key in self.status:
                self.serial.write(f"\r{key} {value}\r".encode())
        self.serial.flush()

if __name__ == "__main__":
    from time import sleep
    from configparser import ConfigParser
    logging.basicConfig( level=logging.DEBUG)

    configString = "[serial]\nport=/dev/ttyACM0\nbaudRate=115200"
    config = ConfigParser()
    config.read_string( configString)
    c = crawler( config)

    sleep(1)
    print(c.status)
