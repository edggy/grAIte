// Websocket Helpers
var GraiteWs = function(url, port) {
  this.ws = null;
  this.createSuccess = false;
  this.userInfo = {
    "username": "",
    "id": "",
    "ants": [],
  };

  this._url = url;
  this._port = port;

  this.connect = function() {
    var loc = "ws://" + this._url;
    if (port != "") {
      loc += ":" + this._port;
    }

    this.ws = new WebSocket(loc)

    this.ws.onopen = function(e) {
      WS.ws.onmessage = function(e) {
        WS.parseResponse(e.data);
      };
    };
  };

  this.requestInfo = function(xi, yi, ti, xf, yf, tf) {
    var msg = {
      Command: "Request",
      Body: {
        "xi": xi,
        "yi": yi,
        "ti": ti,
        "xf": xf,
        "yf": yf,
        "tf": tf
      }
    };

    this.ws.send(JSON.stringify(msg));
  };

  this.parseResponse = function(r) {
    res = JSON.parse(r);

    if (res.Command == "Connect") {
      // signal game to start, finished connecting to server
    } else if (res.Command == "Request") {
      // parse the game state recieved
    } else if (res.Command == "Banned") {
      // user was banned (oh nooo)
      localStorage.clear();
      alert("You have been banned for some reason. Sorry.");
      window.location = "http://google.com/search?q=tissue+paper";
    }
  };
};
