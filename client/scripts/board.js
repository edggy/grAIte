var Tile = function(x, y) {
  this.x = x;
  this.y = y;

  this.sz = CONFIG.sz;

  this.pheromones = 0;
  this.food = 0;

  this.tainted = false;

  this.occupied = false;
  this.actor = null;

  this.update = function(p, f, t, o, a) {
    this.pheromones = p;
    this.food = f;
    this.tainted = t;
    this.occupied = o;
    this.actor = a;
  };

  this.randomize = function() {
    this.pheromones = Math.floor(Math.random()*CONFIG.pmax);
    this.food = Math.floor(Math.random()*CONFIG.fmax);
  };

  this.reset = function() {
    this.pheromones = 0;
    this.food = 0;
  }

  this.getColor = function() {
    let fscale = Math.ceil(CONFIG.fmax/255);
    let r = this.food/fscale;

    let pscale = Math.ceil(CONFIG.pmax/255);
    let b = this.pheromones/pscale;
    return color(r, 0, b);
  };

  this.show = function() {
    fill(this.getColor);
    rect(floor(this.pos.x), floor(this.pos.y), this.sz, this.sz);
  };
};

var Board = function() {
  this.wd = CONFIG.col;
  this.hg = CONFIG.row;

  this.tiles = [];

  for (let y = 0; y < this.hg; y++) {
    let row = [];
    for (let x = 0; x < this.wd; x++) {
      row.push(new Tile(x, y));
    }
    this.tiles.push(row);
  }

  this.get = function(x, y) {
    return this.tiles[y][x];
  };

  this.set = function(x, y, tile) {
    this.tiles[y][x] = tile;
  };
};
