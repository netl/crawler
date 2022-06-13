#!/usr/bin/env python3
import serial
from websocket_server import WebsocketServer
import time
from threading import Thread

cr = serial.Serial('/dev/ttyACM0', 115200)

ws = WebsocketServer(host="0.0.0.0", port=9999)

def on_message(client, server, message):
    print(f"{client}:{message}")
    commands = {
        "forward":"dir 0\nspd 30\n",
        "left":"dir 30\nspd 30\n",
        "right":"dir -30\nspd 30\n",
        "reverse":"spd -30\n",
        "rleft":"dir 30\nspd -30\n",
        "rright":"dir -30\nspd -30\n",
    }
    if message in commands:
        cr.write(commands[message].encode())

clients = []

def new_client(client, server):
    clients.append(client)

def client_disconnect(client, server):
    clients.pop(client)

ws.set_fn_message_received(on_message)
ws.set_fn_new_client(new_client)
ws.set_fn_client_left(client_disconnect)
t = Thread(group=None, target=ws.run_forever)
t.start()

print("ready")
while True:
    crMessage = cr.read(1024)
    for client in clients:
        ws.send_message(client, crMessage)
