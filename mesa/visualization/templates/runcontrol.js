/** runcontrol.js

 Users can reset() the model, advance it by one step(), or run() it through. reset() and
 step() send a message to the server, which then sends back the appropriate data. run() just
 calls the step() method at fixed intervals.

 The model parameters are controlled via the MesaVisualizationControl object.
 */

/**
 * Object which holds visualization parameters.
 *
 * tick: What tick of the model we're currently at
 running: Boolean on whether we have reached the end of the current model
 * fps: Current frames per second.
 */
var MesaVisualizationControl = function() {
    this.tick = -1; // Counts at which tick of the model we are.
    this.running = false; // Whether there is currently a model running
    this.fps = 3; // Frames per second
};

var player; // Variable to store the continuous player
var control = new MesaVisualizationControl();
var elements = [];  // List of Element objects
var model_params = {};

var playPauseButton = $('#play-pause');
var stepButton = $('#step');
var resetButton = $('#reset');


// WebSocket Stuff
var ws = new WebSocket("ws://127.0.0.1:" + port + "/ws"); // Open the websocket connection
ws.onopen = function() {
    console.log("Connection opened!");
    send({"type": "get_params"}); // Request model parameters when websocket is ready
    reset();
};


// Add model parameters that can be edited prior to a model run
var add_params = function() {

    var add_one_param = function(param) {
        // Todo - Implement sliders for min,max and default values
        // Todo - Implement toggles for boolean options
        // Todo - Implement dropdowns for lists
        // Controls should implement a 'submit' routine that sends a message with the parameter name and value.
        // See next line for example, "value" should be handled by the backend visualization element
        // E.x. --> send({"type":"submit_params","param": param_name, "value": value});
        // Todo - implement switch for handling different types

    };

    for (var option in model_params) {
        add_one_param(String(option));
    }
};

/** Parse and handle an incoming message on the WebSocket connection. */
ws.onmessage = function(message) {
    var msg = JSON.parse(message.data);
    switch (msg["type"]) {
        case "viz_state":
            var data = msg["data"];
            for (var i in elements) {
                elements[i].render(data[i]);
            }
            break;
        case "end":
            // We have reached the end of the model
            control.running = false;
            clearInterval(player);
            break;
        case "model_params":
            console.log(msg["params"]);
            model_params = msg["params"]
            add_params();
            break;
        default:
            // There shouldn't be any other message
            console.log("Unexpected message.");
    }
};

/**	 Turn an object into a string to send to the server, and send it. v*/
var send = function(message) {
    msg = JSON.stringify(message);
    ws.send(msg);
};

/** Reset the model, and rest the appropriate local variables. */
var reset = function() {
    control.tick = 0;
    send({"type": "reset"});

    // Reset all the visualizations
    for (var i in elements) {
        elements[i].reset();
    }
};

/** Send a message to the server get the next visualization state. */
var single_step = function() {
    control.tick += 1;
    send({"type": "get_step", "step": control.tick});
};

/** Step the model forward. */
var step = function() {
    if (!control.running) {single_step()}
    else {run()};
};

/** Call the step function at fixed intervals, until getting an end message from the server. */
var run = function() {
    var anchor = $(playPauseButton.children()[0]);
    if (control.running) {
        control.running = false;
        if (player) {
            clearInterval(player);
            player = null;
        }
        anchor.text("Start");
    }
    else {
        control.running = true;
        player = setInterval(single_step, 1000/control.fps);
        anchor.text("Stop");
    }
};

// TODO - implement FPS slider

// Initilaize buttons on top bar
playPauseButton.on('click', run);
stepButton.on('click', step);
resetButton.on('click', reset);
