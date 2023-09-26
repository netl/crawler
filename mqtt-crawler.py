#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from crawler import crawler
import time
from configparser import ConfigParser
import logging
from sys import argv

#configuration
config = ConfigParser()
with open(argv[1],'r') as f:
    config.read_file(f)

#logging
logging.basicConfig( filename = config.get( "log", "logfile"), level=logging.INFO)

#crawler
try:
    cr = crawler(config)
except Exception as E:
    logging.exception(f"exception while setting up crawler\n{E}")
    quit()

publishTopic = config.get( "mqtt", "publishTopic")
def newData(data):
    for topic, value in data.items():
        logging.debug( f">{topic} {value}")
        print( f">{publishTopic}/{topic} {value}")
        #c.publish(f"{publishTopic}/{topic}", str(value))
        c.publish(f"{publishTopic}/{topic}", value)
cr.addHook(newData)

#mqtt client
while True:
    from socket import gaierror
    try:
        print("connecting")
        c = mqtt.Client()
        c.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        c.username_pw_set(config.get( "mqtt", "username"), config.get( "mqtt", "userpass"))
        c.connect( config.get( "mqtt", "host"), config.getint( "mqtt", "port"))
        c.subscribe( config.get( "mqtt", "listenTopic") + "/#")
        print("connected")
        break
    except gaierror as E:
        logging.warning(f"mqtt: {E}")
        time.sleep(1)
        continue
    except Exception as E:
        logging.exception(f"exception while setting up mqtt\n{E}")
        quit()

def on_message(client, userdata, message):
    topic = message.topic.split('/')[-1]
    value = message.payload.decode('utf-8')
    output = {topic:value}
    logging.debug( f"<{topic} {value}")
    print( f"<{topic} {value}")
    cr.setCAN(output)
c.on_message = on_message

c.loop_start()

#main 
logging.info( "ready")
print("ready")
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

#stop threads
logging.info( "stopping!")
cr.stop()
c.loop_stop()
