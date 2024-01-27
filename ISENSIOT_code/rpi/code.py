import serial
import time
import datetime
import requests
import socket
import asyncio
import websockets
from colourDetection import *

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# log-in
URL = "http://192.168.56.175:8080/api/v1"
BODY = {"email": "appeltaart@gmail.com", "password": "appeltaart"}
Headers = {"Keep-Alive":"False" }
r = requests.get(url=URL+"/auth/login", json=BODY)
data = r.json()
JWT = data["token"]
Headers = {"Authorization": "Bearer "+JWT, "Keep-Alive":"False"}

# post lan ip
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
BODY = s.getsockname()[0]
r = requests.post(url=URL+"/frituur/1", json=BODY, headers=Headers)
s.close()


import asyncio
import websockets
from datetime import datetime
on = False
batch = -404
timeStamp = 0
colour = '#%02x%02x%02x' % tuple(takeImage().astype(int))

# todo make handler
async def handler(websocket):
    while True:
        global on
        global timeStamp
        task = await websocket.recv()
        print("received: {task:s}".format(task=task))
        if task == "on":
            print("test on")
            on = True
            r = requests.post(url=URL+"/batch/1", headers=Headers)
            data = r.json()
            global batch
            batch = data
            await websocket.send(str(batch))
            ser.write(b"aan")


        if task == "off":
            timeStamp = 0
            on = False
            ser.write(b"uit")

# todo make loop
async def sensorLoop():
    global timeStamp
    while True:
        start = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        if on:
            timeStamp += 1
            # take info from arduino
            count = 1
            line = ser.readline().decode('utf-8').rstrip()
            [temp, spin] = [float(i) for i in line.split(" ")]
            # send info to database
            BODY = {"temperature": temp, "colour": colour, "viscosity": spin}
            requests.post(url=URL + "/timerecording/" + str(batch) + "/" + str(timeStamp), json=BODY, headers=Headers, timeout=5)
        else:
            ser.reset_input_buffer()
        end = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        await asyncio.sleep(13+start-end)


# create some sort of background task to update the time.
asyncio.get_event_loop().create_task(sensorLoop())

start_server = websockets.serve(handler, "", 1234)

asyncio.get_event_loop().run_until_complete(start_server)
print("server started")
asyncio.get_event_loop().run_forever()



