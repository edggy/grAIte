// Initial setup for everything
function setup() {
  // Initialize global variables
  BOARD = new Board();
  WS = new GraiteWs(CONFIG.wsurl, CONFIG.wsport)

  // make the canvas
  createCanvas(CONFIG.wd, CONFIG.hg);

  // connect to server
  if (!DEV) {
    WS.connect();
  }

  // set up the board

  // create the actors
};

// Get input from the player
var input = function() {
  // move reference frame

  // resize board

  // check active ant
};

// Update everything
var update = function() {
  // poll server for info on visible ants and board

  // update the information

  // update the board

  // update the actors
};

// Draw everything visible to screen
function draw() {
  // get this stuff out of the way
  input();
  update();

  // on to actually drawing everything

  // draw the background
  background(CONFIG.bgclr);

  // draw the board

  // draw the actors

  // draw the tooltip background

  // draw the tooltip text
};
