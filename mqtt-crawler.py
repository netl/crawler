#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import serial
import time

#serial port
cr = serial.Serial('/dev/ttyACM0', 115200)

#mqtt client
c = mqtt.Client()
c.connect('raptor.local')
c.publish("/crawler/status", "hello")
c.subscribe("/crawler/command/#")
def on_message(client, userdata, message):
    topic = message.topic.split('/')[-1]
    value = message.payload.decode('utf-8')
    output = f"{topic} {value}\r"
    print(output)
    cr.write(output.encode())
c.on_message = on_message

#main 
print("ready")
while True:

    #check for data on serial port
    crMessage = cr.read(1024)
    if crMessage:
        try:
            for line in crMessage.decode('utf-8').split('\n'):
                tm = line.split(' ')
                c.publish(f"/crawler/status/{tm[0]}", tm[1])
        except IndexError:
            pass

    #check mqtt messages
    c.loop_read()
