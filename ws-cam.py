#!/usr/bin/env python3

from crawler import crawler
from threading import Timer ,Thread
from websocket_server import WebsocketServer
import time
import json
import os

class Camera():
    def __init__(self, crawler, ws, config):
        self.cr = crawler
        self.cr.addHook(self.update_status)
        self.config = config
        self.ws = ws
        #camera
        self.snap_dir = self.config.get("webcam", "directory")
        self.cam_view = [120,120]

    def snapshot(self, name=None):
        resolution = "-video_size 2592x1944 "
        if not name:
            name = int(time.time())
        elif name == "preview":
            resolution = "-video_size 640x480"

        os.system(f"ffmpeg -y -f video4linux2 {resolution} -i /dev/video0 -vframes 1 {self.snap_dir}/{name}.jpg")
        self.ws.send_message_to_all(json.dumps({"image":str(name)}))

    def on_message(self, client, server, message):
        #determine click location relative to current camera position
        #TODO: get position from a database based on image id
        x,y = json.loads(message)
        x = 0.5-x
        y = y-0.5
        new_x = int(max(-90, min( self.cr.status["yaw"]+self.cam_view[0]*x, 90)))
        new_y = int(max(-90, min( self.cr.status["pitch"]+self.cam_view[0]*y, 90)))

        #adjust camera
        target = {"yaw":new_x,"pitch":new_y}
        print(target)
        self.cr.set(target)
        time.sleep(1) # wait for servos to turn

        #take picture
        self.snapshot("preview")

    def update_status(self, data):
        self.ws.send_message_to_all(json.dumps(data))

if __name__ == "__main__":
    #configuration
    from configparser import ConfigParser
    config = ConfigParser()
    with open("crawler.conf",'r') as f:
        config.read_file(f)

    #crawler
    cr = crawler(config)

    #websocket
    ws = WebsocketServer( host = config.get( "websockets", "host"), port = config.getint( "websockets", "port"))

    #camera
    c = Camera(cr, ws, config)

    #websocket thread
    ws.set_fn_message_received(c.on_message)
    t = Thread(group=None, target=ws.run_forever)
    t.start()

    print("ready!")
    #record timelapse
    while True:
        try:
            time.sleep(60)
            c.snapshot()
        except KeyboardInterrupt:
            break

    #cleanup
    ws.shutdown_gracefully()
    t.join()
    cr.stop()
