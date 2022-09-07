import serial
from threading import Thread

class crawler():
    def __init__( self , config):
        self.serial = serial.Serial( config.get( "serial", "port"), config.getint( "serial", "baudRate"))
        self.serialBuffer = b''
        self.status = {}
        self.hooks = [] #list of hooks to call when new data is available

        #thread seutp
        self.run = True
        self.mainThread = Thread(target=self.serialMonitor)
        self.mainThread.start()

    def serialMonitor(self):
        #if self.serial.in_waiting:
        while self.run:
            try:
                self.serialBuffer += self.serial.read(max(1,self.serial.in_waiting))
            except serial.serialutil.SerialException as E:
                #spamming too much?
                print(E)
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

    configString = "[serial]\nport=/dev/ttyACM0\nbaudRate=115200"
    config = ConfigParser()
    config.read_string( configString)
    c = crawler( config)

    sleep(1)
    print(c.status)
