import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import requests

afbeelding = cv.imread('stock_images/pan_met_water.jpg')

percentage = 0.60

# converteer de BGR waarden
# naar RGB zodat matplotlib ermee kan werken
afbeelding = cv.cvtColor(afbeelding, cv.COLOR_BGR2RGB)







URL = "http://192.168.134.142:8080/api/v1/auth/login"
BODY = {"email": "apppeltaart@gmail.com", "password": "appeltaart"}


r = requests.get(url=URL, json=BODY)
data = r.json()

BODY = {"temperature": 44, "colour": "Yellow", "viscosity": 44}
