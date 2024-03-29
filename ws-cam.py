#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from websocket_server import WebsocketServer
import time
import json
import os
import threading

class Camera():
    def __init__(self, mq, ws, config):

        #mqtt
        self.mq = mq
        self.mq.on_message = self.on_mq_message
        self.crawlerTopic = config.get( "mqtt", "listenTopic")
        self.crawlerPubTopic = config.get( "mqtt", "publishTopic")

        #websocket
        self.ws = ws

        #camera
        self.snap_dir = config.get("webcam", "directory")
        self.cam_view = [120,120]
        self.cam_status = {"pitch":0, "yaw":0}
        self.newest_image = None

        #time lapse
        self.run = True
        self.timelapse()

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
        self.take_picture("preview", "640x480")

    def on_ws_client(self, client):
        self.ws.send_message(client, json.dumps({"image":self.newest_image}))

    def on_mq_message(self, client, userdata, message):
        topic = message.topic.split('/')[-1]
        value = message.payload.decode('utf-8')

        if topic == "image":
            self.newest_image = value

        output = {topic:value}
        self.cam_status.update(output)
        self.update_status(output)

    def update_status(self, data):
        self.ws.send_message_to_all(json.dumps(data))

    def take_picture(self, name=None, videoSize = "2592x1944"):
        if not name:
            name = int(time.time())

        os.system(f"curl localhost:8080/snapshot > {self.snap_dir}/{name}.jpg")
        #os.system(f"ffmpeg -y -f video4linux2 -video_size {videoSize} -i /dev/video0 -vframes 1 {self.snap_dir}/{name}.jpg")
        self.mq.publish(f"{self.crawlerPubTopic}/image", name)
        self.ws.send_message_to_all(json.dumps({"image":str(name)}))

    def timelapse(self, period = 60):
        self.take_picture()
        if self.run:
            t = threading.Timer(period, self.timelapse, args=(period,)).start()

if __name__ == "__main__":
    #configuration
    from configparser import ConfigParser
    from sys import argv
    config = ConfigParser()
    with open(argv[1],'r') as f:
        config.read_file(f)

    #mqtt
    while True:
        from socket import gaierror
        try:
            mq = mqtt.Client()
            mq.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
            mq.username_pw_set(config.get( "mqtt", "username"), config.get( "mqtt", "userpass"))
            mq.connect( config.get( "mqtt", "host"), config.getint( "mqtt", "port"))
            mq.subscribe( config.get( "mqtt", "publishTopic") + "/#")
            mq.loop_start()
            break
        except ( gaierror, OSError ) as E:
            time.sleep(1)
            print(E)
            continue
        except Exception as E:
            raise

    #websocket
    ws = WebsocketServer( host = config.get( "websockets", "host"), port = config.getint( "websockets", "port"))

    #camera
    c = Camera(mq, ws, config)
    ws.set_fn_message_received(c.on_ws_message)
    #ws.set_fn_new_client(c.on_ws_client)

    #websocket main loop
    ws.run_forever()

    #cleanup
    c.run = False
    ws.shutdown_gracefully()
    mq.loop_stop()
