#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from websocket_server import WebsocketServer
import time
import json
import os

class Camera():
    def __init__(self, mq, ws, config):

        #mqtt
        self.mq = mq
        self.mq.on_message = self.on_mq_message
        self.crawlerTopic = config.get( "mqtt", "listenTopic")

        #websocket
        self.ws = ws

        #camera
        self.snap_dir = config.get("webcam", "directory")
        self.cam_view = [120,120]
        self.cam_status = {"pitch":0, "yaw":0}

    def on_ws_message(self, client, server, message):
        #determine click location relative to current camera position
        x,y = json.loads(message)
        x = 0.5-x
        y = y-0.5
        new_x = int(max(-90, min( int(self.cam_status["yaw"])+self.cam_view[0]*x, 90)))
        new_y = int(max(-90, min( int(self.cam_status["pitch"])+self.cam_view[1]*y, 90)))


        #send new position over mqtt
        print(f"aiming at {new_x}, {new_y}")
        for key, value in {"yaw":new_x,"pitch":new_y}.items():
            self.mq.publish(f"{self.crawlerTopic}/{key}", value)

        # wait for servos to turn
        time.sleep(1) 

        #take picture
        name = "preview"
        os.system(f"ffmpeg -y -f video4linux2 -video_size 640x480 -i /dev/video0 -vframes 1 {self.snap_dir}/{name}.jpg")
        self.ws.send_message_to_all(json.dumps({"image":str(name)}))

    def on_mq_message(self, client, userdata, message):
        topic = message.topic.split('/')[-1]
        value = message.payload.decode('utf-8')
        output = {topic:value}
        self.cam_status.update(output)
        self.update_status(output)

    def update_status(self, data):
        self.ws.send_message_to_all(json.dumps(data))

if __name__ == "__main__":
    #configuration
    from configparser import ConfigParser
    from sys import argv
    config = ConfigParser()
    with open(argv[1],'r') as f:
        config.read_file(f)

    #mqtt
    mq = mqtt.Client()
    mq.connect( config.get( "mqtt", "host"), config.getint( "mqtt", "port"))
    mq.subscribe( config.get( "mqtt", "publishTopic") + "/#")
    mq.loop_start()

    #websocket
    ws = WebsocketServer( host = config.get( "websockets", "host"), port = config.getint( "websockets", "port"))

    #camera
    c = Camera(mq, ws, config)
    ws.set_fn_message_received(c.on_ws_message)

    #websocket main loop
    ws.run_forever()

    #cleanup
    ws.shutdown_gracefully()
    mq.loop_stop()
