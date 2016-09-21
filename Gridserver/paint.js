
function initialize() {
	var cnv = document.getElementById("cnv");

	var gridOptions = {
		lines : {
			separation : 25,
			color : '#D0D0D0',
			min : 15,
			max : 200
		},
		width : cnv.width,
		height : cnv.height,
		canvas : cnv,
		cells : {},
		startX : 0,
		startY : 0,
		power : {
			current : 1.0,
			max : 1.0,
			min : 0.01,
			delta : 8.0
		},
		buffer: 50
	};

	gridOptions.ws = new WebSocket("ws://cloudvm.mine.nu/ws");
	
	gridOptions.ws.onmessage = function (e) {
		onMessage(e, gridOptions)
	};
	
	gridOptions.ws.onopen = function (e) {
		requestData({
			'startX' : gridOptions.startX - gridOptions.buffer,
			'startY' : gridOptions.startY - gridOptions.buffer,
			'endX' : gridOptions.endX + gridOptions.buffer,
			'endY' : gridOptions.endY + gridOptions.buffer
		}, gridOptions)
	};
	
	//gridOptions.ws.onclose = function(e){console.log('Socket Closed')};

	// Register an event listener to call the resizeCanvas() function
	// each time the window is resized.
	window.addEventListener('resize', function () {
		resizeCanvas(gridOptions)
	}, false);
	
	window.addEventListener("keypress", function (e) {
		onKeypress(e, gridOptions)
	}, false);
	
	window.addEventListener("keydown", function (e) {
		onKeydown(e, gridOptions)
	}, false);
	
	window.addEventListener("click", function (e) {
		onClick(e, gridOptions)
	}, false);
	
	//window.addEventListener("click", function(e){onClick(e, gridOptions)}, false);
	window.addEventListener("mousemove", function (e) {
		onMouseMove(e, gridOptions);
	}, false);
	
	window.addEventListener("mousewheel", function (e) {
		MouseWheelHandler(e, gridOptions)
	}, false);
	
	window.addEventListener("DOMMouseScroll", function (e) {
		MouseWheelHandler(e, gridOptions)
	}, false);

	/*window.setInterval(function () {
		requestData({
			'startX' : gridOptions.startX - gridOptions.buffer,
			'startY' : gridOptions.startY - gridOptions.buffer,
			'endX' : gridOptions.endX + gridOptions.buffer,
			'endY' : gridOptions.endY + gridOptions.buffer
		}, gridOptions)
	}, 5000);*/
	

	// Draw canvas for the first time.
	resizeCanvas(gridOptions);
}

function zoom(amount, gridOptions) {
	gridOptions.lines.separation += amount;
	if (gridOptions.lines.separation > gridOptions.lines.max)
		gridOptions.lines.separation = gridOptions.lines.max;
	else if (gridOptions.lines.separation < gridOptions.lines.min)
		gridOptions.lines.separation = gridOptions.lines.min;
	
	calcGrid(gridOptions);
	gridOptions.buffer = Math.ceil(Math.max(gridOptions.numCellsX, gridOptions.numCellsY) / 2)
	redraw(gridOptions);
}

function MouseWheelHandler(e, gridOptions) {

	// cross-browser wheel delta
	var e = window.event || e; // old IE support
	var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
	zoom(delta, gridOptions)
}

function onMouseMove(e, gridOptions) {
	gridOptions.mouseX = e.clientX;
	gridOptions.mouseY = e.clientY;
	
	if(gridOptions.mouseX < 15) {
		move({'x':-1}, gridOptions);
	}
	else if(gridOptions.mouseX > gridOptions.width-15) {
		move({'x':1}, gridOptions);
	}
	
	if(gridOptions.mouseY < 15) {
		move({'y':-1}, gridOptions);
	}
	else if(gridOptions.mouseY > gridOptions.height-15) {
		move({'y':1}, gridOptions);
	}
}

function onKeypress(e, gridOptions) {
	//console.log('onKeypress')
	if (e.keyCode == 43 || e.keyCode == 61) {
		// + or =
		zoom(1, gridOptions);
	} else if (e.keyCode == 45) {
		// -
		zoom(-1, gridOptions);
	} else if (e.keyCode == 32) {
		// Space
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			toggleCell(cell, gridOptions);
		}
	} else if (e.keyCode == 122) {
		// Z
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			blendCellColor(cell, '', gridOptions);
		}
	} else if (e.keyCode == 120) {
		// X
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			blendCellColor(cell, '#000000', gridOptions);
		}
	} else if (e.keyCode == 99) {
		// C
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			blendCellColor(cell, '#FF0000', gridOptions);
		}
	} else if (e.keyCode == 118) {
		// V
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			blendCellColor(cell, '#00FF00', gridOptions);
		}
	} else if (e.keyCode == 98) {
		// B
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			blendCellColor(cell, '#0000FF', gridOptions);
		}
	} else if (e.keyCode == 113) {
		//Q
		gridOptions.power.current += 1.0 / gridOptions.power.delta;
		if (gridOptions.power.current > gridOptions.power.max)
			gridOptions.power.current = 1;
	} else if (e.keyCode == 97) {
		//A
		gridOptions.power.current -= 1.0 / gridOptions.power.delta;
		if (gridOptions.power.current < gridOptions.power.min)
			gridOptions.power.current = gridOptions.power.min;
	} else if (e.keyCode == 119) {
		//W
		gridOptions.power.delta /= 2;
		if (gridOptions.power.delta < 2)
			gridOptions.power.delta = 2;
	} else if (e.keyCode == 115) {
		//S
		gridOptions.power.delta *= 2;
		if (gridOptions.power.delta > 128)
			gridOptions.power.delta = 128;
	}

}

function move(amount, gridOptions) {
	amount.x = amount.x || 0;
	amount.y = amount.y || 0;
	
	gridOptions.startX += amount.x;
	gridOptions.startY += amount.y;
	
	calcGrid(gridOptions);

	if(amount.x < 0 && gridOptions.cells[gridOptions.startX - gridOptions.buffer] == undefined) {
		requestData({
				'startX' : gridOptions.startX - gridOptions.buffer,
				'startY' : gridOptions.startY - gridOptions.buffer,
				'endX' : gridOptions.startX,
				'endY' : gridOptions.endY + gridOptions.buffer
			}, gridOptions);
	}
	else if(amount.x > 0 && gridOptions.cells[gridOptions.endX + gridOptions.buffer] == undefined) {
		requestData({
				'startX' : gridOptions.endX, 
				'startY' : gridOptions.startY - gridOptions.buffer,
				'endX' : gridOptions.endX + gridOptions.buffer,
				'endY' : gridOptions.endY + gridOptions.buffer
			}, gridOptions);
	}
	
	if(amount.y < 0 && (gridOptions.cells[gridOptions.startX] == undefined  || gridOptions.cells[gridOptions.startX][gridOptions.startY - gridOptions.buffer])) {
		requestData({
				'startX' : gridOptions.startX - gridOptions.buffer,
				'startY' : gridOptions.startY - gridOptions.buffer,
				'endX' : gridOptions.endX + gridOptions.buffer,
				'endY' : gridOptions.startY
			}, gridOptions);
	}
	else if(amount.y > 0 && (gridOptions.cells[gridOptions.startX] == undefined || gridOptions.cells[gridOptions.startX][gridOptions.endY + gridOptions.buffer])) {
		requestData({
				'startX' : gridOptions.startX - gridOptions.buffer, 
				'startY' : gridOptions.endY,
				'endX' : gridOptions.endX + gridOptions.buffer,
				'endY' : gridOptions.endY + gridOptions.buffer
			}, gridOptions);
	}
	redraw(gridOptions);
}

function onKeydown(e, gridOptions) {
	if (e.keyCode == 37) {
		//Left
		move({'x':-1}, gridOptions);
	} else if (e.keyCode == 39) {
		//Right
		move({'x':1}, gridOptions);
	} else if (e.keyCode == 38) {
		//Up
		move({'y':-1}, gridOptions);
	} else if (e.keyCode == 40) {
		//Down
		move({'y':1}, gridOptions);
	} else if (e.keyCode == 27) {
		//Esc
		alert('Controls:\n \
		Left Click: Toggle One Color\n \
		Arrow Keys: Move\n \
		Space:      Toggle Colors\n \
		Z:          Clear\n \
		X:          Black\n \
		C:          Red\n \
		V:          Green\n \
		B:          Blue\n \
		Q:          Darken\n \
		A:          Lighten\n \
		W:          Fine Tune +\n \
		S:          Fine Tune -\n')
	}
}

function onClick(e, gridOptions) {
	var x = e.clientX;
	var y = e.clientY;

	var cell = getCellAt(x, y, gridOptions);

	toggleCell(cell, gridOptions);
}

function blendRGBColors(p, c0, c1) {
	c0 = c0 || '#FFFFFF';
	c1 = c1 || '#FFFFFF';

	var color0 = {};
	var color1 = {};
	
	color0.r = parseInt(c0[1] + c0[2], 16);
	color0.g = parseInt(c0[3] + c0[4], 16);
	color0.b = parseInt(c0[5] + c0[6], 16);
	
	color1.r = parseInt(c1[1] + c1[2], 16);
	color1.g = parseInt(c1[3] + c1[4], 16);
	color1.b = parseInt(c1[5] + c1[6], 16);

	var newColor = {}
	for (var c in color0) {
		newColor[c] = Math.ceil(color0[c] * p + color1[c] * (1 - p));
		if (newColor[c] < 0x10)
			newColor[c] = 0;
		if (newColor[c] > 0xF0)
			newColor[c] = 0xFF;
		var hex = newColor[c].toString(16);
		if (hex.length < 2) {
			hex = '0' + hex;
		}
		newColor[c] = hex;
		if (newColor[c].length > 2)
			newColor[c] = 'FF';
	}

	return ('#' + newColor.r + newColor.g + newColor.b).toUpperCase();
}

function setCellColor(cell, color, gridOptions) {
	cell.color = color;
	if (cell.color == '#FFFFFF')
		cell.color = '';
	submitData(cell.x, cell.y, gridOptions);
	redraw(gridOptions);
}

function blendCellColor(cell, color, gridOptions) {
	var newColor = blendRGBColors(gridOptions.power.current, color, cell.color);
	setCellColor(cell, newColor, gridOptions);
}

function toggleCell(cell, gridOptions) {

	if (cell.color == '#000000') {
		blendCellColor(cell, '#FF0000', gridOptions);
	} else if (cell.color == '#FF0000') {
		blendCellColor(cell, '#00FF00', gridOptions);
	} else if (cell.color == '#00FF00') {
		blendCellColor(cell, '#0000FF', gridOptions);
	} else if (cell.color == '#0000FF') {
		blendCellColor(cell, '', gridOptions);
	} else if (cell.color == '#FFFFFF' || cell.color == undefined || cell.color == '') {
		blendCellColor(cell, '#000000', gridOptions);
	}

}

function getCellAtMouse(gridOptions) {
	return getCellAt(gridOptions.mouseX, gridOptions.mouseY, gridOptions)
}

function getCellAt(x, y, gridOptions) {
	var sep = gridOptions.lines.separation;

	var cellX = Math.floor(x / sep) + gridOptions.startX;
	var cellY = Math.floor(y / sep) + gridOptions.startY;

	if (gridOptions.cells[cellX] == undefined) {
		gridOptions.cells[cellX] = {}
	}

	if (gridOptions.cells[cellX][cellY] == undefined) {
		gridOptions.cells[cellX][cellY] = {};
	}
	gridOptions.cells[cellX][cellY].x = cellX;
	gridOptions.cells[cellX][cellY].y = cellY;

	return gridOptions.cells[cellX][cellY];
}

function resizeCanvas(gridOptions) {
	//console.log('resizeCanvas')
	var cnv = gridOptions.canvas;
	cnv.width = window.innerWidth;
	cnv.height = window.innerHeight;
	gridOptions.width = cnv.width;
	gridOptions.height = cnv.height;

	redraw(gridOptions);
}

function redraw(gridOptions) {
	var cnv = gridOptions.canvas;
	cnv.getContext('2d').clearRect(0, 0, cnv.width, cnv.height);

	drawCells(gridOptions);
	drawGridLines(gridOptions);

}

function drawGridLines(gridOptions) {
	var cnv = gridOptions.canvas;
	var ctx = cnv.getContext('2d');

	var iWidth = cnv.width;
	var iHeight = cnv.height;
	var sep = gridOptions.lines.separation;

	ctx.strokeStyle = gridOptions.lines.color;
	ctx.strokeWidth = 1;

	ctx.beginPath();

	var iCount = null;
	var i = null;
	var x = null;
	var y = null;

	iCount = Math.floor(iWidth / sep);

	for (i = 1; i <= iCount; i++) {
		x = (i * sep);
		ctx.moveTo(x, 0);
		ctx.lineTo(x, iHeight);
		ctx.stroke();
	}

	iCount = Math.floor(iHeight / sep);

	for (i = 1; i <= iCount; i++) {
		y = (i * sep);
		ctx.moveTo(0, y);
		ctx.lineTo(iWidth, y);
		ctx.stroke();
	}

	ctx.closePath();

	return;
}

function calcGrid(gridOptions) {
	gridOptions.width = gridOptions.canvas.width;
	gridOptions.height = gridOptions.canvas.height;
	gridOptions.numCellsX = Math.ceil(gridOptions.width / gridOptions.lines.separation);
	gridOptions.numCellsY = Math.ceil(gridOptions.height / gridOptions.lines.separation);
	gridOptions.endX = gridOptions.startX + gridOptions.numCellsX;
	gridOptions.endY = gridOptions.startY + gridOptions.numCellsY;
}

function drawCells(gridOptions) {
	var cnv = gridOptions.canvas;
	var ctx = cnv.getContext('2d');

	calcGrid(gridOptions);
	
	var sep = gridOptions.lines.separation;
	var iWidth = gridOptions.width;
	var iHeight = gridOptions.height;
	var startX = gridOptions.startX;
	var startY = gridOptions.startY;
	var numCellsX = gridOptions.numCellsX;
	var numCellsY = gridOptions.numCellsY;

	//requestData({'startX':startX, 'startY':startY, 'endX':startX + numCellsX, 'endY':startY + numCellsY}, gridOptions);

	for (var x = 0; x <= numCellsX; x++) {
		for (var y = 0; y <= numCellsX; y++) {
			if (gridOptions.cells[x + startX] == undefined)
				continue;
			if (gridOptions.cells[x + startX][y + startY] == undefined)
				continue;

			var cell = gridOptions.cells[x + startX][y + startY];

			if (cell.color == undefined || cell.color == '')
				ctx.fillStyle = '#FFFFFF';
			else
				ctx.fillStyle = cell.color;

			ctx.fillRect(x * sep, y * sep, sep, sep);
		}
	}
	return;
}

function onMessage(e, gridOptions) {
	//console.log('recieved:\t' + e.data)
	var toks = e.data.split('\t');

	if (toks[0] == 'set') {
		var cells = JSON.parse(toks[1]);
		for (x in cells) {
			for (y in cells[x]) {
				if (gridOptions.cells[x] == undefined) {
					gridOptions.cells[x] = {}
				}
				gridOptions.cells[x][y] = cells[x][y];
			}
		}
		redraw(gridOptions);
	}
}

function requestData(range, gridOptions) {
	var ws = gridOptions.ws;

	if (ws.readyState == 1) {
		ws.send('get\t' + JSON.stringify(range))
	}

}

function submitData(x, y, gridOptions) {
	var ws = gridOptions.ws;

	var data = gridOptions.cells[x][y];
	data.x = x;
	data.y = y;

	if (ws.readyState == 1) {
		ws.send('set\t' + JSON.stringify(data))
	}
}

