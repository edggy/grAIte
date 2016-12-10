var drawText = function(str, x, y) {
  textSize(CONFIG.txtsz);
  fill(COLORS.txtclr);
  text(str, x, y);
};

var drawTextCull = function(str, x, y, wd, hg) {
  textSize(CONFIG.txtsz);
  fill(COLORS.txtclr);
  text(str, x, y, x+wd, y+hg);
};
