#!/usr/bin/env python3
import socket
import serial
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('0.0.0.0', 2323))
s.listen(5)
s.settimeout(0)
s.setblocking(0)

cr = serial.Serial('/dev/ttyACM0', 115200)

print("ready")
while True:
    crMessage = cr.read(1024)
    try:
        if crMessage:
            connection.send(crMessage)
        message = connection.recv(1024)
        if message:
            cr.write(message.replace(b'\n',b'\r'))
            print(message)
    except (BrokenPipeError, NameError): 
        try:
            connection, address = s.accept()
            connection.settimeout(0)
        except (TimeoutError, BlockingIOError): 
            pass
    except (BlockingIOError):
        pass
