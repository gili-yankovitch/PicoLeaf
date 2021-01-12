#!/usr/bin/python3

import os
# from requests import get, post, put
import requests as rq
from flask import Flask, request, Response, render_template
from json import dumps
from struct import pack

CREATE_URL = "https://jsonstorage.net/api/items"
RETRIEVE_URL = "https://jsonstorage.net/api/items/"
ID = "952953a2-b326-4ed4-8807-ed0b06ac88e2"

RETRIEVE_URL = "https://api.npoint.io/"
ID = "c20179a77bb32cab79d1"

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
	data = request.get_json()

	print("Received:")
	print(data)
	
	# res = rq.put("/".join((RETRIEVE_URL, ID)), headers =  {"content-type": "application/json"}, json = data).json()
	res = rq.post("/".join((RETRIEVE_URL, ID)), headers =  {"content-type": "application/json"}, json = data).json()

	version += 1

	return dumps(res)

@app.route("/get", methods = ["GET"])
def _get():
	data = rq.get("/".join((RETRIEVE_URL, ID))).json()

	response = bytes()
	response += pack("BB", VALID_CODE, version) # Version

	if "animation" not in data or "colors" not in data:
		return "\x00Invalid data", 400

	if data["animation"] == "still":
		frames = 1
		brightnessStart = 16
		brightnessAdd = 0
		offset_colors_per_frame = 0
		sleepMs = 100
	elif data["animation"] == "breathing":
		frames = 32
		brightnessStart = 1
		brightnessAdd = 1
		offset_colors_per_frame = 0
		sleepMs = 40
	elif data["animation"] == "sliding":
		frames = len(data["colors"])
		brightnessStart = 16
		brightnessAdd = 0
		offset_colors_per_frame = 1
		sleepMs = 100

	beginOffset = 0
	ledsNum = len(data["colors"])
	brightness = brightnessStart

	for frameIdx in range(frames):
		beginOffset = (beginOffset + offset_colors_per_frame) % ledsNum

		if (data["animation"] == "breathing") and frameIdx == int(frames / 2):
			brightnessAdd = -1

		response += pack("B", OPCODE_FRAME_START)

		for ledIdx in range(ledsNum):
			val = data["colors"][(beginOffset + ledIdx) % ledsNum]

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

	# print("Response len: %d" % len(response))

	return response

@app.route("/getText", methods = ["GET"])
def _getText():
	data = rq.get("/".join((RETRIEVE_URL, ID))).json()

	print("Data:", data)
	
	return dumps(data)

@app.route("/", methods = ["GET"])
def root():
	return render_template("index.html")