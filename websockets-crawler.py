#!/usr/bin/env python3
from crawler import crawler
from websocket_server import WebsocketServer
import time
from threading import Thread
import json

#crawler
cr = crawler('/dev/ttyACM0')

def newData(data):
    for topic, value in data.items():
        ws.send_message_to_all(json.dumps(data))
cr.addHook(newData)

#websockets
ws = WebsocketServer(host="0.0.0.0", port=9999)

def on_message(client, server, message):
    print(f"{client}:{message}")
    commands = {
        "forward":{"dir":0,"spd":30},
        "left":{"dir":30,"spd":30},
        "right":{"dir":-30,"spd":30},
        "reverse":{"dir":0,"spd":-30},
        "rleft":{"dir":30,"spd":-30},
        "rright":{"dir":-30,"spd":-30},
    }
    #TODO verify the message is something we're expecting
    try:
        variable, value = message.split(" ")
        commands.update({
            "pitch":{variable:value},
            "yaw":{variable:value}
            })
    except ValueError:
        #most likely got a direction command instead of pitch/yaw
        if message in commands:
            variable = message
        else:
            print(message)
            raise

    cr.set(commands[variable])

def new_client(client, server):
    print(f"new client: {client}")

def client_disconnect(client, server):
    print(f"client dropped: {client}")

ws.set_fn_message_received(on_message)
ws.set_fn_new_client(new_client)
ws.set_fn_client_left(client_disconnect)
t = Thread(group=None, target=ws.run_forever)
t.start()

print("ready")
while True:
    try:
        time.sleep(1)
        print(cr.status)
    except KeyboardInterrupt:
        break

#stop threads
print("stopping!")
ws.shutdown_gracefully()
t.join()
cr.stop()
