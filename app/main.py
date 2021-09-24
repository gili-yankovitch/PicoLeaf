#!/usr/bin/python3

import os
import requests as rq
from werkzeug.utils import secure_filename
from flask import Flask, request, Response, render_template, send_from_directory, make_response, send_file
from flask_cors import CORS, cross_origin
from json import dumps
from struct import pack
from datetime import datetime

app = Flask(__name__,
	static_folder = 'static')
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods = ["GET"])
@app.route("/<path:path>", methods = ["GET"])
# @cross_origin()
def root(**args):
	if "path" not in args:
		path = None
	else:
		path = args["path"]

	if path == "" or path is None:
		path = "index.html"

	print("Path = %s" % path)

	response = make_response(send_from_directory("static", secure_filename(path)))
	response.headers["Access-Control-Allow-Origin"] = "*"
	response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept";
	response.headers["Access-Control-Allow-Methods"] = "PUT, POST, GET, DELETE, OPTIONS";

	return response
