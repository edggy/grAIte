DEV = true; // switch to false eventually

// Singleton
var COLORS = new function() {
  this.white = [240, 240, 240];
  this.lgray = [192, 192, 192];
  this.gray = [128, 128, 128];
  this.dgray = [64, 64, 64];
  this.black = [16, 16, 16];

  this.red = [240, 16, 16];
  this.green = [16, 240, 16];
  this.blue = [16, 16, 240];

  this.orange = [240, 128, 48];
  this.purple = [192, 64, 240];
  this.yellow = [240, 240, 80];

  this.cyan = [240, 240, 16];
  this.pink = [240, 128, 208];

  this.bluegreen = [48, 224, 144];
  this.yellowgreen = [160, 224, 80];

  this.brown = [128, 96, 64];

  this._getCXM = function(type, h, s, lv) {
    out = {};
    if (type == "hsl") {
      out.c = s * (1 - Math.abs(2*l));
      out.x = c * (1 - Math.abs((h/60 % 2) - 1));
      out.m = l - c/2;
    } else if (type == "hsv") {
      out.c = v * s;
      out.x = c * (1 - Math.abs((h/60 % 2) - 1));
      out.m = v - c;
    }

    return out;
  };

  this.fromHSL = function(h, s, l) {
    return this._fromHSLV("hsl", h, s, l);
  };

  this.fromHSV = function(h, s, v) {
    return this._fromHSLV("hsv", h, s, v);
  };

  this._fromHSLV = function(type, h, s, lv) {
    if (h < 0 || h >= 360 || s < 0 || s > 1 || l < 0 || l > 1) {
      if (DEV) {
        console.log("Invalid hslv color: " + h + s + l);
      }
      return null;
    }

    var cxm = this._getCXM(type, h, s, l);
    var c = cxm.c;
    var x = cxm.x;
    var m = cxm.m;

    c = (c+m)*255;
    x = (x+m)*255;
    var O = m*255;

    if (0 <= h < 60) {
      return [c, x, O];
    } else if (60 <= h < 120) {
      return [x, c, O];
    } else if (120 <= h < 180) {
      return [O, c, x];
    } else if (180 <= h < 240) {
      return [O, x, c];
    } else if (240 <= h < 300) {
      return [x, O, c];
    } else if (300 <= h < 360) {
      return [c, O, x];
    }
  };

  this.fromCYMK = function(c, m, y, k) {
    if (c < 0 || c > 1 || m < 0 || m > 1 || y < 0 || y > 1 || k < 0 || k > 1) {
      if (DEV) {
        console.log("Invalid hslv color: " + h + s + l);
      }
      return null;
    }
    var r = 255 * (1-c) * (1-k);
    var g = 255 * (1-m) * (1-k);
    var b = 255 * (1-y) * (1-k);
    return [r, g, b];
  };
}();

// Singleton
var CONFIG = new function() {
  this.sz = 32;
  this.wd = 640;
  this.hg = 480;

  this.fmax = 4294967295;
  this.pmax = 4294967295;

  this.col = this.wd/this.sz;
  this.row = this.hg/this.sz;

  this.bgclr = COLORS.black;
  this.guiclr = COLORS.white;

  this.txtsz = 16;
  this.txtclr = COLORS.black;

  this.timestep = 1; // 1 move per second
  this.autoplay = true;

  this.wsurl = "127.0.0.1";
  this.wsport = "8080";
}();

var ALLPLAYERS = {};
var ALLANTS = {};
var BOARD;
var WS;
