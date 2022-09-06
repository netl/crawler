#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from crawler import crawler
import time

#crawler
cr = crawler('/dev/ttyACM0')

def newData(data):
    for topic, value in data.items():
        c.publish(f"/crawler/status/{topic}", value)
cr.addHook(newData)

#mqtt client
c = mqtt.Client()
c.connect('raptor.local')
c.publish("/crawler/status", "hello")
c.subscribe("/crawler/command/#")

def on_message(client, userdata, message):
    topic = message.topic.split('/')[-1]
    value = message.payload.decode('utf-8')
    output = {topic:value}
    print(output)
    cr.set(output)
c.on_message = on_message

c.loop_start()

#main 
print("ready")
while True:
    try:
        time.sleep(1)
        print(cr.status)
    except KeyboardInterrupt:
        break

#stop threads
print("stopping!")
cr.stop()
c.loop_stop()
