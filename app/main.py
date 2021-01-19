#!/usr/bin/python3

import os
# from requests import get, post, put
import requests as rq
import configparser
from flask import Flask, request, Response, render_template
from json import dumps
from struct import pack

CREATE_URL = "https://jsonstorage.net/api/items"
RETRIEVE_URL = "https://jsonstorage.net/api/items/"
ID = "952953a2-b326-4ed4-8807-ed0b06ac88e2"

RETRIEVE_URL = "https://api.npoint.io/"
ID = "c20179a77bb32cab79d1"

ledData = None
version = 0
VALID_CODE = 0x42

OPCODE_FRAME_START = 0
OPCODE_FRAME_END   = 1
OPCODE_SLEEP       = 2
OPCODE_LED         = 3

app = Flask(__name__,
	static_folder = 'static',
	template_folder='templates')

def _createStore(data):
	return rq.post(CREATE_URL, headers = {"content-type": "application/json"}, json = data).json()

@app.route("/update", methods = ["POST"])
def _update():
	global version
	global ledData
	ledData = request.get_json()

	# Add version
	ledData["version"] = version

	res = rq.post("/".join((RETRIEVE_URL, ID)), headers =  {"content-type": "application/json"}, json = ledData).json()

	version += 1

	print("Version: %d" % version)

	return dumps(res)

@app.route("/get", methods = ["GET"])
def _get():
	global ledData
	global version

	# Read animation config
	config = configparser.ConfigParser()
	config.read("animations.ini")

	if ledData is None:
		ledData = rq.get("/".join((RETRIEVE_URL, ID))).json()

		if "version" in ledData:
			version = ledData["version"]

	response = bytes()
	response += pack("BB", VALID_CODE, version & 0xff) # Version

	if "animation" not in ledData or "colors" not in ledData:
		return "\x00Invalid data", 400

	frames = int(config[ledData["animation"]]["frames"])

	if frames == 0:
		frames = len(ledData["colors"])
	brightnessStart = int(config[ledData["animation"]]["brightnessStart"])
	brightnessAdd = int(config[ledData["animation"]]["brightnessAdd"])
	offsetColorsPerFrame = int(config[ledData["animation"]]["offsetColorsPerFrame"])
	sleepMs = int(config[ledData["animation"]]["sleepMs"])
	endSleep = int(config[ledData["animation"]]["endSleep"])

	beginOffset = 0
	ledsNum = len(ledData["colors"])
	brightness = brightnessStart

	for frameIdx in range(frames):
		beginOffset = (beginOffset + offsetColorsPerFrame) % ledsNum

		if (ledData["animation"] == "breathing") and frameIdx == int(frames / 2):
			brightnessAdd = -1

		response += pack("B", OPCODE_FRAME_START)

		for ledIdx in range(ledsNum):
			val = ledData["colors"][(beginOffset + ledIdx) % ledsNum]

			if "red" not in val:
				continue

			if "green" not in val:
				continue

			if "blue" not in val:
				continue

			response += pack("BBBBB", OPCODE_LED, abs(val["red"]), abs(val["green"]), abs(val["blue"]), abs(brightness))

		response += pack("B", OPCODE_FRAME_END)

		response += pack("BB", OPCODE_SLEEP, sleepMs)

		brightness += brightnessAdd

	while endSleep > 255:
		response += pack("BB", OPCODE_SLEEP, 255)
		endSleep -= 255

	response += pack("BB", OPCODE_SLEEP, endSleep)
	# print("Response len: %d" % len(response))

	return response

@app.route("/getText", methods = ["GET"])
def _getText():
	global ledData

	ledData = rq.get("/".join((RETRIEVE_URL, ID))).json()

	print("Data:", ledData)
	
	return dumps(ledData)

@app.route("/", methods = ["GET"])
def root():
	return render_template("index.html")
