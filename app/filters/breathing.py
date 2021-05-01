#!/usr/bin/python3
from app.animation import Animation

def init(colors):
	animation = Animation(colors, 15, 40, 750)

	initFrame = animation.createFrame()

	initFrame.setBrightness(1)

	return animation

def frame(animation):
	nextFrame = animation.createFrame()

	nextFrame.addBrightness(-1 if animation.currentFrameNum() > 8 else 1)

	return animation
