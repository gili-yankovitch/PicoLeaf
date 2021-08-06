#!/usr/bin/python3
from app.main import app, socketio

if __name__ == "__main__":
	#app.run("0.0.0.0", port = 80)
	socketio.run(app, "0.0.0.0", port = 80)
