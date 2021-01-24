#!/usr/bin/python3
from app.animation import Animation
from math import floor, ceil

LEDS_PER_FRAME = 6
FRAMES_FOR_ANIMATION = 31

redDiff = 0
greenDiff = 0
blueDiff = 0

def init(colors):
	global redDiff
	global greenDiff
	global blueDiff

	animation = Animation(colors, FRAMES_FOR_ANIMATION, 40, 750)

	initFrame = animation.createFrame()

	initFrame.setBrightness(16)

	# Calculate the "gradient-step"
	redStart = colors[0]["red"]
	redEnd = colors[LEDS_PER_FRAME * 2]["red"]
	redDiff = (redEnd - redStart) / FRAMES_FOR_ANIMATION

	if (redDiff < 0):
		redDiff = int(ceil(redDiff))
	else:
		redDiff = int(floor(redDiff))

	greenStart = colors[0]["green"]
	greenEnd = colors[LEDS_PER_FRAME * 2]["green"]
	greenDiff = (greenEnd - greenStart) / FRAMES_FOR_ANIMATION

	if (greenDiff < 0):
		greenDiff = int(ceil(greenDiff))
	else:
		greenDiff = int(floor(greenDiff))

	blueStart = colors[0]["blue"]
	blueEnd = colors[LEDS_PER_FRAME * 2]["blue"]
	blueDiff = (blueEnd - blueStart) / FRAMES_FOR_ANIMATION

	if (blueDiff < 0):
		blueDiff = int(ceil(blueDiff))
	else:
		blueDiff = int(floor(blueDiff))

	# print(redDiff, greenDiff, blueDiff)

	return animation

def frame(animation):
	nextFrame = animation.createFrame()

	direction = -1 if animation.currentFrameNum() > ((FRAMES_FOR_ANIMATION + 1) / 2) else 1

	nextFrame.addColors(redDiff * direction, greenDiff * direction, blueDiff * direction)

	return animation
