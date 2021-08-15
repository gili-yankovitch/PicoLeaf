#!/usr/bin/python3

import os
# from requests import get, post, put
import requests as rq
import configparser
from werkzeug.utils import secure_filename
from flask import Flask, request, Response, render_template, send_from_directory
from flask_socketio import SocketIO
from json import dumps
from struct import pack
from datetime import datetime
from . import filters

CREATE_URL = "https://jsonstorage.net/api/items"
RETRIEVE_URL = "https://jsonstorage.net/api/items/"
ID = "952953a2-b326-4ed4-8807-ed0b06ac88e2"

RETRIEVE_URL = "https://api.npoint.io/"
ID = "c20179a77bb32cab79d1"

ledData = None
version = 0
VALID_CODE = 0x42


app = Flask(__name__,
	static_folder = 'static',
	template_folder='templates')

socketio = SocketIO(app)

clients = []

schedule = {
		23: "off",
		 0: "off",
		 1: "off",
		 2: "off",
		 3: "off",
		 4: "off",
		 5: "off",
		 6: "off",
		 7: "off"
	}

def _sendConnectedClients(data):
	socketio.emit("output", data, broadcast = True)
	return
	disconnected = []
	print("Distributing updates to connected clients...")
	for client in clients:
		print("Sending to client: %s" % client)
		try:
			socketio.emit("output", data, room = client)
		except:
			disconnected.append(client)

	for client in disconnected:
		clients.remove(client)
	print("Done!")

@socketio.on("connect")
def connection():
	global clients
	print("Client connected: %s" % request.sid)
	# clients.append(request.sid)

@socketio.on("disconnect")
def disconnection():
	global clients
	print("Client disconnected: %s" % request.sid)
	#clients.remove(request.sid)

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

	# Send signal to all clients
	_sendConnectedClients("*")

	return dumps(res)

@app.route("/get", methods = ["GET"])
def _get():
	global ledData
	global version

	if ledData is None:
		ledData = rq.get("/".join((RETRIEVE_URL, ID))).json()

		if "version" in ledData:
			version = ledData["version"]

	# Get current hour
	hour = datetime.now().hour

	if hour in schedule:
		print("Changing to %s as scheduled" % schedule[hour])
		ledData["animation"] = schedule[hour]
		version = 255
	elif version == 255:
		# Just when it's out of schedule, restart version counter
		version = 0

	response = bytes()
	response += pack("BB", VALID_CODE, version & 0xff) # Version

	if "animation" not in ledData or	\
		"colors" not in ledData or		\
		ledData["animation"] not in filters.filters:
		print("Invalid data")
		return "\x00Invalid data", 400

	animation = filters.filters[ledData["animation"]].init(ledData["colors"])

	for frameIdx in animation:
		frame = filters.filters[ledData["animation"]].frame(animation)

	# print(animation)

	return response + animation.encode()

@app.route("/getText", methods = ["GET"])
def _getText():
	global ledData

	ledData = rq.get("/".join((RETRIEVE_URL, ID))).json()

	print("Data:", ledData)

	return dumps(ledData)

@app.route("/", methods = ["GET"])
@app.route("/<path:path>", methods = ["GET"])
def root(**args):
	if "path" not in args:
		path = None
	else:
		path = args["path"]

	if path == "" or path is None:
		path = "index.html"

	print("Path = %s" % path)

	return send_from_directory("static", secure_filename(path))
	# return render_template(path)
