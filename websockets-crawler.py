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
        "forward":"\rdir 0\rspd 30\r",
        "left":"\rdir 30\rspd 30\r",
        "right":"\rdir -30\rspd 30\r",
        "reverse":"\rdir 0\rspd -30\r",
        "rleft":"\rdir 30\rspd -30\r",
        "rright":"\rdir -30\rspd -30\r",
    }
    if message in commands:
        cr.write(commands[message].encode())

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
    crMessage = cr.read(1024)
    if crMessage:
        for client in ws.clients:
            ws.send_message(client, crMessage)
