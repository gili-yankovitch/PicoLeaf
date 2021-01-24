#!/usr/bin/python3
from app.animation import Animation
from math import floor, ceil

LEDS_PER_FRAME = 6
FRAMES_FOR_ANIMATION = 31

diffs = []

def init(colors):
	animation = Animation(colors, FRAMES_FOR_ANIMATION, 40, 750)

	initFrame = animation.createFrame()

	initFrame.setBrightness(16)

	# Calculate the "gradient-step"
	for led, idx in zip(colors, range(len(colors))):
		redStart = colors[idx]["red"]
		redEnd = colors[(idx + LEDS_PER_FRAME * 3) % len(colors)]["red"]
		redDiff = (redEnd - redStart) / (FRAMES_FOR_ANIMATION / 2)

		if (redDiff < 0):
			redDiff = int(ceil(redDiff))
		else:
			redDiff = int(floor(redDiff))

		greenStart = colors[idx]["green"]
		greenEnd = colors[(idx + LEDS_PER_FRAME * 3) % len(colors)]["green"]
		greenDiff = (greenEnd - greenStart) / (FRAMES_FOR_ANIMATION / 2)

		if (greenDiff < 0):
			greenDiff = int(ceil(greenDiff))
		else:
			greenDiff = int(floor(greenDiff))

		blueStart = colors[idx]["blue"]
		blueEnd = colors[(idx + LEDS_PER_FRAME * 3) % len(colors)]["blue"]
		blueDiff = (blueEnd - blueStart) / (FRAMES_FOR_ANIMATION / 2)

		if (blueDiff < 0):
			blueDiff = int(ceil(blueDiff))
		else:
			blueDiff = int(floor(blueDiff))

		diffs.append({"red": redDiff * 2, "green": greenDiff * 2, "blue": blueDiff * 2})

	# print(redDiff, greenDiff, blueDiff)

	return animation

def frame(animation):
	nextFrame = animation.createFrame()

	direction = -1 if animation.currentFrameNum() > ((FRAMES_FOR_ANIMATION) / 2) else 1

	for led, idx in zip(nextFrame, range(len(diffs))):
		led.add(diffs[idx]["red"] * direction,
			diffs[idx]["green"] * direction,
			diffs[idx]["blue"] * direction)

	return animation
