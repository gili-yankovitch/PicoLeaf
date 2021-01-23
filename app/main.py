#!/usr/bin/python3

import os
# from requests import get, post, put
import requests as rq
import configparser
from flask import Flask, request, Response, render_template
from json import dumps
from struct import pack
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

	if ledData is None:
		ledData = rq.get("/".join((RETRIEVE_URL, ID))).json()

		if "version" in ledData:
			version = ledData["version"]

	response = bytes()
	response += pack("BB", VALID_CODE, version & 0xff) # Version

	if "animation" not in ledData or	\
		"colors" not in ledData or		\
		ledData["animation"] not in filters.filters:
		return "\x00Invalid data", 400

	animation = filters.filters[ledData["animation"]].init(ledData["colors"])

	for frameIdx in animation:
		frame = filters.filters[ledData["animation"]].frame(animation)

	return response + animation.encode()

@app.route("/getText", methods = ["GET"])
def _getText():
	global ledData

	ledData = rq.get("/".join((RETRIEVE_URL, ID))).json()

	print("Data:", ledData)

	return dumps(ledData)

@app.route("/", methods = ["GET"])
def root():
	return render_template("index.html")
