// Development functions (mostly a server simulation)
// yay mock objects

var populateTiles = function(density, x1, y1, x2, y2) {
  var temp;
  if (x1 > x2) {
    temp = x1;
    x1 = x2;
    x2 = temp;
  }

  if (y1 > y2) {
    temp = y1;
    y1 = y2;
    y2 = temp;
  }

  var wd = x2 - x1;
  var hg = y2 - y1;
  for (let i = y1; i < y2; i++) {
    for (let j = x1; j < x2; j++) {
      if (Math.random()*100 < density) {
        BOARD.get(x, y).randomize();
      } else {
        BOARD.get(x, y).reset();
      }
    }
  }
};

var populateAnts = function(num, x1, y1, x2, y2) {
  var temp;
  if (x1 > x2) {
    temp = x1;
    x1 = x2;
    x2 = temp;
  }

  if (y1 > y2) {
    temp = y1;
    y1 = y2;
    y2 = temp;
  }

  var dx = x2 - x1;
  var dy = y2 - y1;
  for (let i = 0; i < num; i++) {
    let id = uuid();
    let antX = x1 + Math.floor(Math.random()*dx);
    let antY = y1 + Math.floor(Math.random()*dy);
    let _ = new Ant(id, antX, antY); // ant inserts itself into ALLANTS
    _.energy = Math.floor(Math.random()*100);
  }
};
