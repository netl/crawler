#!/usr/bin/python3
import paho.mqtt.client as mqtt
import time
import logging
from configparser import ConfigParser
from sys import argv
import can

mapping = {
    0x010 + 8 + 0 :{ "topic"      :"battery/voltage", "scalar":20/4096, "offset":0   },
    0x010 + 8 + 1 :{ "topic"      :"battery/current", "scalar":40/4096, "offset":-10 },
    "velocity"    :{ "arbitration":0x010 + 0        , "scalar":1000   , "offset":1000},
    "steering"    :{ "arbitration":0x010 + 1        , "scalar":1000   , "offset":1000},
    "camera/pitch":{ "arbitration":0x010 + 2        , "scalar":1000   , "offset":1000},
    "camera/yaw"  :{ "arbitration":0x010 + 3        , "scalar":1000   , "offset":1000},
}

#configuration
config = ConfigParser()
with open(argv[1],'r') as f:
    config.read_file(f)

#logging
logging.basicConfig(level=logging.INFO)

#canbus
bus = can.ThreadSafeBus(interface='socketcan', channel='can0', bitrate=500000)

#mqtt client
mq = mqtt.Client()
baseTopic = config.get( "mqtt", "baseTopic")
while True:
    from socket import gaierror
    try:
        print("connecting")
        mq.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        mq.username_pw_set(config.get( "mqtt", "username"), config.get( "mqtt", "userpass"))
        mq.connect( config.get( "mqtt", "host"), config.getint( "mqtt", "port"))
        mq.subscribe( baseTopic + "#")
        print("connected")
        break
    except gaierror as E:
        logging.warning(f"mqtt: {E}")
        time.sleep(1)
        continue
    except Exception as E:
        logging.exception(f"exception while setting up mqtt\n{E}")
        quit()

#generic scaling routine
def scale(value, o):
    scalar = o["scalar"]
    offset = o["offset"]
    return value * scalar + offset

#process incoming MQTT data
def MQTTReceive(client, userdata, message):
    topic = message.topic[len(baseTopic):]
    value = float(message.payload.decode('utf-8'))
    logging.debug(f"{topic}:{value}")
    if topic in mapping:
        CANSend(topic, value)
mq.on_message = MQTTReceive

#canbus -> mqtt
def MQTTSend(arbitration, value):
    try:
        #calculate
        result = scale(value, mapping[arbitration])
    
        #send
        topic = mapping[arbitration]["topic"]
        logging.info(f"{arbitration:03X}->{topic}:{result}") 
        mq.publish(baseTopic+topic, result)

    except KeyError:
        logging.warning(f"invalid arbitration: {arbitration:03X}")
    
    except Exception as e:
        logging.error(e)

#mqtt -> canbus
def CANSend(topic, value):
    try:
        #calculate
        result = int(scale(value, mapping[topic]))

        #send
        arbitration = mapping[topic]["arbitration"]
        msg = can.Message(is_extended_id=False)
        msg.data = result.to_bytes(2,"big")
        msg.arbitration_id = arbitration
        msg.dlc = 2
        logging.info(f"{topic}->{arbitration:03X}:{result:04X}")
        bus.send(msg)

    except KeyError:
        logging.warning(f"invalid topic: {topic}")
    
    except Exception as e:
        logging.error(e)

#start receiving over mqtt
mq.loop_start()

#monitor canbus and send everything over MQTT
while True:
    msg = bus.recv()
    logging.debug(f"{msg.arbitration_id}:{msg.data}")

    # parse bytes to a single value TODO: make this cleaner
    value = msg.data[1]*pow(2,8) + msg.data[0]

    MQTTSend(msg.arbitration_id, value)
