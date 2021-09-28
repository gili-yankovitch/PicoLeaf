// Const values
var NUM_TRIANGLES = 4;
var LEDS_PER_COLOR = 6;

var endpointsServiceAssets = "http://central-endpoints.herokuapp.com/get";
var endpointsServiceUpdate = "http://central-endpoints.herokuapp.com/update";

// Grab the select box
let inventoryTag;

let endpointsDict = {};

function notifyDevice(address)
{
	// Notify device
	$.ajax({
		type: "POST",
		url: "http://" + address + "/update",
		success: function ()
		{
			console.log("Update done");
		}
	});
}

function refreshAnimation()
{
	notifyDevice(endpointsDict[inventoryTag.value]["address"]);
}

function getEndpoints(callback)
{
	$.get(
		endpointsServiceAssets,
		{
			"id": "HOME_DESK"
		},
		(data) => {
			var parsed = JSON.parse(data);

			for (var idx in parsed)
			{
				endpointsDict[parsed[idx]["name"]] = parsed[idx];
			}

			callback(endpointsDict);
		}
	)
}

function updateEndpoint(endpointId, endpointName, data)
{
	// Update the DB data
	$.ajax({
		type: "POST",
		url: endpointsServiceUpdate,
		data: JSON.stringify({"id": endpointId, "name": endpointName, "data": JSON.stringify(data)}),
		success: function ()
		{
			console.log("Posting to: " + "http://" + endpointsDict[endpointName]["address"] + "/update");

			notifyDevice(endpointsDict[endpointName]["address"]);

		},
		contentType: "application/json",
		dataType: "json"
	});
}

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

function _isList(obj)
{
	if ((typeof(obj) == "object") && ("push" in obj))
		return true;

	return false;
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

function createTriangles(num, sendUpdate)
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

	var hexColors = []

	for (var idx in colorPut)
	{
		hexColors.push(rgbToHex("rgb(" + colorPut[idx]["red"] + "," + colorPut[idx]["green"] + "," + colorPut[idx]["blue"] + ")"));
	}

	var output = {"animation": $("input[name='animation']:checked").val(), "colors": hexColors};

	// Update data
	console.log(output);

	if (sendUpdate)
	{
		updateEndpoint(endpointsDict[inventoryTag.value]["id"],
			endpointsDict[inventoryTag.value]["name"],
			output);
	}
}

function updateUI(name, sendUpdate)
{
	if (typeof(endpointsDict[name]["data"]) == "string")
	{
		data = endpointsDict[name]["data"].replace("\\\"", "\"");

		data = JSON.parse(data);
	}
	else
	{
		data = endpointsDict[name]["data"];
	}

	if (typeof(data) != "object")
	{
		return;
	}

	if (!_isList(data["colors"]))
	{
		// At least double it
		data["colors"] = [data["colors"], data["colors"]];
	}

	for (var idx in data["colors"])
	{
		if ((typeof(data["colors"][idx]) == "string") && (data["colors"][idx][0] == '#'))
		{
			data["colors"][idx] = hexToRGB(data["colors"][idx]);
		}
	}

	$('#' + data["animation"]).prop("checked", true);

	console.log("Animation: " + data["animation"]);

	// data = {"colors": data};

	$('#picker0').tinycolorpicker().data('plugin_tinycolorpicker').setColor("rgb(" + data["colors"][0]["red"] + ", " + data["colors"][0]["green"] + ", " + data["colors"][0]["blue"] + ")");
	$('#picker1').tinycolorpicker().data('plugin_tinycolorpicker').setColor("rgb(" + data["colors"][data["colors"].length - 1]["red"] + ", " + data["colors"][data["colors"].length - 1]["green"] + ", " + data["colors"][data["colors"].length - 1]["blue"] + ")");

	createTriangles(NUM_TRIANGLES, sendUpdate);
}

function endpointSelected(obj)
{
	updateUI(obj.target.value, false);
}

function createEndpointTag(endpoint)
{
	var endpointTag = document.createElement('option');
	endpointTag.setAttribute("value", endpoint["name"]);
	endpointTag.innerText = endpoint["alias"];

	inventoryTag.appendChild(endpointTag);
}

function populateEndpoints()
{
	var inventory = document.getElementById('inventory');

	getEndpoints((endpoints) =>
		{
			var first = "";

			for (const idx in endpoints)
			{
				createEndpointTag(endpoints[idx]);

				if (first == "")
				{
					first = endpoints[idx]["name"];
				}
			}

			if (first != "")
			{
				inventory.value = first;

				updateUI(inventory.value, false);
			}
		}
	);

	inventory.onchange = endpointSelected;
}

$(document).ready(function() {
	console.log("Init");

	inventoryTag = document.getElementById('inventory');

	createPicker("pickers", "picker0", function(event) {
		console.log("Color #0: " + $('#picker0').tinycolorpicker().data('plugin_tinycolorpicker').colorHex);

		createTriangles(NUM_TRIANGLES, true);
	});

	createPicker("pickers", "picker1", function(event) {
		console.log("Color #1: " + $('#picker1').tinycolorpicker().data('plugin_tinycolorpicker').colorHex);

		createTriangles(NUM_TRIANGLES, true);
	});

	$('#picker0')[0].style.marginRight = "50px";
	$('#picker1')[0].style.marginLeft = "50px";

	$("input[name='animation']").change(function (event) {
		createTriangles(NUM_TRIANGLES, true);
	});

	populateEndpoints();

	$("#title").click(refreshAnimation);
});
