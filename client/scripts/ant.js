var Ant = function(idString, x, y) {
  this.idString = idString;
  ALLPLAYERS[isString] = this;
  this.energy = 0;

  this.pos = createVector(x, y);
  this.sz = CONFIG.sz;

  this.show = function() {
    fill(240);
    rect(floor(this.pos.x), floor(this.pos.y), 2, this.sz*2);
  };

  this.update = function(x, y) {
    this.pos.x = x;
    this.pos.y = y;
  };

  this.kill = function() {
    delete ALLANTS[this.idString];
  };
};
