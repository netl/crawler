#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from crawler import crawler
import time
from configparser import ConfigParser

#configuration
config = ConfigParser()
with open("crawler.conf",'r') as f:
    config.read_file(f)

#crawler
cr = crawler(config)

publishTopic = config.get( "mqtt", "publishTopic")
def newData(data):
    for topic, value in data.items():
        c.publish(f"{publishTopic}/{topic}", value)
cr.addHook(newData)

#mqtt client
c = mqtt.Client()
c.connect( config.get( "mqtt", "host"), config.getint( "mqtt", "port"))
c.subscribe( config.get( "mqtt", "listenTopic") + "/#")

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
