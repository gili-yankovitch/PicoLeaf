// Const values
var NUM_TRIANGLES = 4;
var LEDS_PER_COLOR = 6;

function createPicker(parentId, newId, callback)
{
	var colorPicker = document.createElement("div");
	colorPicker.setAttribute("id", newId);
	colorPicker.setAttribute("class", "colorPicker");

	var color = document.createElement("a");
	color.setAttribute("class", "color");

	var colorInner = document.createElement("div");
	colorInner.setAttribute("class", "colorInner");

	var track = document.createElement("div");
	track.setAttribute("class", "track");

	var dropdown = document.createElement("ul");
	dropdown.setAttribute("class", "dropdown");

	var option = document.createElement("li");

	var colorInput = document.createElement("input");
	colorInput.setAttribute("type", "hidden");
	colorInput.setAttribute("class", "colorInput");

	colorPicker.appendChild(color);
	colorPicker.appendChild(track);
	colorPicker.appendChild(dropdown);
	colorPicker.appendChild(colorInput);

	color.appendChild(colorInner);

	dropdown.appendChild(option);

	document.getElementById(parentId).appendChild(colorPicker);

	var obj = $("#" + newId);

	obj.tinycolorpicker();
	obj.change(callback);
}

function hexToRGB(hex)
{
	var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);

	return { "red": parseInt(result[1], 16), "green": parseInt(result[2], 16), "blue": parseInt(result[3], 16) };
}

function hex(x)
{
	var digits = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F");
	return isNaN(x) ? "00" : digits[(x - x % 16 ) / 16] + digits[x % 16];
}

function rgbToHex(rgb)
{
	var result = rgb.match(/\d+/g);

	function hex(x)
	{
		var digits = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F");
		return isNaN(x) ? "00" : digits[(x - x % 16 ) / 16] + digits[x % 16];
	}

	return "#" + hex(result[0]) + hex(result[1]) + hex(result[2]);
}

function createTriangles(num)
{
	var canvas = document.getElementById("canvas");

	if (window.innerWidth > 480)
	{
		var side = 100;
		var buffer = 10;
	}
	else
	{
		var side = 90;
		var buffer = 9;
		canvas.width = 300;
	}

	var total_width = num * (side + buffer) / 2;

	var x = (canvas.width - total_width - side / 2) / 2;
	var y = 25;
	var height = Math.sqrt(Math.pow(side, 2) - Math.pow(side/2, 2))

	// Calculate the gradient
	var colorStart = $('#picker0').tinycolorpicker().data('plugin_tinycolorpicker').colorHex;
	if (colorStart == "")
		colorStart = "#ffffff";

	colorStart = hexToRGB(colorStart);

	var colorEnd = $('#picker1').tinycolorpicker().data('plugin_tinycolorpicker').colorHex;
	if (colorEnd == "")
		colorEnd = "#ffffff";

	colorEnd = hexToRGB(colorEnd);

	console.log("Color #0: " + colorStart);
	console.log("Color #1: " + colorEnd);

	var redDiff = Math.floor((colorStart["red"] - colorEnd["red"]) * (-1) / (num - 1));
	var greenDiff = Math.floor((colorStart["green"] - colorEnd["green"]) * (-1) / (num - 1));
	var blueDiff = Math.floor((colorStart["blue"] - colorEnd["blue"]) * (-1) / (num - 1));

	console.log("Diff: " + redDiff + ", " + greenDiff + ", " + blueDiff);

	var colorPut = [];

	if (canvas.getContext)
	{
		var ctx = canvas.getContext("2d");

		for (i = 0; i < num; ++i)
		{
			ctx.beginPath();

			ctx.fillStyle = "#" + hex(colorStart["red"] + redDiff * i) + hex(colorStart["green"] + greenDiff * i) + hex(colorStart["blue"] + blueDiff * i);
			// console.log("Iter #" + i + ": " + ctx.fillStyle);

			for (var j = 0; j < LEDS_PER_COLOR; ++j)
			{
				colorPut.push({ "red": colorStart["red"] + redDiff * i, "green": colorStart["green"] + greenDiff * i, "blue": colorStart["blue"] + blueDiff * i});
			}

			ctx.lineWidth = "2";

			if (i % 2 == 0)
			{
				ctx.moveTo(x, y);

				x += side;
				ctx.lineTo(x, y);

				x -= side / 2;
				y += height;
				ctx.lineTo(x, y);

				x -= side / 2
				y -= height;
				ctx.lineTo(x, y);

				x += side;
			}
			else
			{
				ctx.moveTo(x, y);

				x += side / 2;
				y += height;
				ctx.lineTo(x, y);

				x -= side;
				ctx.lineTo(x, y);

				x += side / 2;
				y -= height;
				ctx.lineTo(x, y);
			}

			ctx.stroke();
			ctx.fill();

			// Buffer
			x += buffer;

		}
	}

	var output = {"animation": $("input[name='animation']:checked").val(), "colors": colorPut};

	console.log(output);

	// Post twice to catch other replicas on server
	for (var updateIdx = 0; updateIdx < 2; ++updateIdx)
	{
		$.ajax({
			type: "POST",
			url: "/update",
			data: JSON.stringify(output),
			success: function ()
			{
				console.log("Update done");
			},
			contentType: "application/json",
			dataType: "json"
		});
	}
}

$(document).ready(function() {
	console.log("Init");

	createPicker("pickers", "picker0", function(event) {
		console.log("Color #0: " + $('#picker0').tinycolorpicker().data('plugin_tinycolorpicker').colorHex);

		createTriangles(NUM_TRIANGLES);
	});

	createPicker("pickers", "picker1", function(event) {
		console.log("Color #1: " + $('#picker1').tinycolorpicker().data('plugin_tinycolorpicker').colorHex);

		createTriangles(NUM_TRIANGLES);
	});

	$('#picker0')[0].style.marginRight = "50px";
	$('#picker1')[0].style.marginLeft = "50px";

	$("input[name='animation']").change(function (event) {
		createTriangles(NUM_TRIANGLES);
	});

	initColors = $.get("/getText", function (data, status, jqXHR)
	{
		data = JSON.parse(data);

		$('#' + data["animation"]).prop("checked", true);

		console.log("Animation: " + data["animation"]);

		// data = {"colors": data};

		$('#picker0').tinycolorpicker().data('plugin_tinycolorpicker').setColor("rgb(" + data["colors"][0]["red"] + ", " + data["colors"][0]["green"] + ", " + data["colors"][0]["blue"] + ")");
		$('#picker1').tinycolorpicker().data('plugin_tinycolorpicker').setColor("rgb(" + data["colors"][data["colors"].length - 1]["red"] + ", " + data["colors"][data["colors"].length - 1]["green"] + ", " + data["colors"][data["colors"].length - 1]["blue"] + ")");


		createTriangles(NUM_TRIANGLES);
	});
});
