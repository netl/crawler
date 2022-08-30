#!/usr/bin/env python3
import serial
from websocket_server import WebsocketServer
import time
from threading import Thread

cr = serial.Serial('/dev/ttyACM0', 115200)

ws = WebsocketServer(host="0.0.0.0", port=9999)

def on_message(client, server, message):
    print(f"{client}:{message}")
    #TODO verify the message is something we're expecting
    commands = {
        "forward":"\rdir 0\rspd 30\r",
        "left":"\rdir 30\rspd 30\r",
        "right":"\rdir -30\rspd 30\r",
        "reverse":"\rdir 0\rspd -30\r",
        "rleft":"\rdir 30\rspd -30\r",
        "rright":"\rdir -30\rspd -30\r",
        "pitch":f"\r{message}\r",
        "yaw":f"\r{message}\r",
    }
    m = message.split()[0]
    if m in commands:
        cr.write(commands[m].encode())

def new_client(client, server):
    print(f"new client: {client}")

def client_disconnect(client, server):
    print(f"client dropped: {client}")

ws.set_fn_message_received(on_message)
ws.set_fn_new_client(new_client)
ws.set_fn_client_left(client_disconnect)
t = Thread(group=None, target=ws.run_forever)
t.start()

crMessage = b""
print("ready")
while True:
    crMessage += cr.read(1024)
    if crMessage:
        packets = crMessage.split(b'\r\n')[:-1]
        crMessage = crMessage.split(b'\r\n')[-1]
        for packet in packets:
            ws.send_message_to_all(packet.decode("utf-8"))
