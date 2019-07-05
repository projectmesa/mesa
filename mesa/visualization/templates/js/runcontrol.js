/* runcontrol.js
 Users can reset() the model, advance it by one step(), or start() it. reset() and
 step() send a message to the server, which then sends back the appropriate data.
 start() just calls the step() method at fixed intervals.

 The model parameters are controlled via the ModelController object.
*/

/*
 * Variable definitions
 */
const controller = new ModelController();
const vizElements = [];
const startModelButton = document.getElementById("play-pause");
const stepModelButton = document.getElementById("step");
const resetModelButton = document.getElementById("reset");
const stepDisplay = document.getElementById("currentStep");


/**
 * A ModelController that defines the model state.
 * @param  {number} tick=0 - Initial step of the model
 * @param  {number} fps=3 - Run the model with this number of frames per second
 * @param  {boolean} running=false - Initialize the model in a running state?
 * @param  {boolean} finished=false - Initialize the model in a finished state?
 */
function ModelController(tick = 0, fps = 3, running = false, finished = false) {
    this.tick = tick;
    this.fps = fps;
    this.running = running;
    this.finished = finished;

    /** Start the model and keep it running until stopped */
    this.start = function start() {
        this.running = true;
        this.step();
        startModelButton.firstElementChild.innerText = "Stop";
    }

    /** Stop the model */
    this.stop = function stop() {
        this.running = false;
        startModelButton.firstElementChild.innerText = "Start";
    }

    /**
     * Step the model one step ahead.
     *
     * If the model is in a running state this function will be called repeatedly
     * after the visualization elements are rendered. */
    this.step = function step() {
        this.tick += 1;
        stepDisplay.innerText = this.tick;
        send({ type: "get_step", step: this.tick });
    }

    /** Reset the model and visualization state but keep its running state */
    this.reset = function reset() {
        this.tick = 0;
        stepDisplay.innerText = this.tick;
        // Reset all the visualizations
        vizElements.forEach(element => element.reset());
        if (this.finished) {
            this.finished = false;
            startModelButton.firstElementChild.innerText = "Start";
        }
        clearTimeout(this.timeout)
        send({ type: "reset" });
    }

    /** Stops the model and put it into a finished state */
    this.done = function done() {
        this.stop();
        this.finished = true;
        startModelButton.firstElementChild.innerText = "Done";
    }

    /**
     * Render visualisation elements with new data.
     * @param {any[]} data Model state data passed to the visualization elements
     */
    this.render = function render(data) {
        vizElements.forEach((element, index) => element.render(data[index]))
        if (this.running) {
            this.timeout = setTimeout(() => this.step(), 1000 / this.fps);
        }
    }

    /**
     * Update the frames per second
     * @param {number} val - The new value of frames per second
     */
    this.updateFPS = function (val) {
        this.fps = Number(val);
    }
}

/*
 * Set up the the FPS control
 */
const fpsControl = $("#fps").slider({
    max: 20,
    min: 0,
    value: controller.fps,
    ticks: [0, 20],
    ticks_labels: [0, 20],
    ticks_position: [0, 100]
});
fpsControl.on("change", () => controller.updateFPS(fpsControl.val()));


/*
 * Button logic for start, stop and reset buttons
 */
startModelButton.onclick = () => {
    if (controller.running) {
        controller.stop();
    } else if (!controller.finished) {
        controller.start();
    }
};
stepModelButton.onclick = () => {
    if (!controller.running & !controller.finished) {
        controller.step();
    }
};
resetModelButton.onclick = () => controller.reset();

/*
 * Websocket opening and message handling
 */

/** Open the websocket connection; support TLS-specific URLs when appropriate */
const ws = new WebSocket(
    (window.location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws"
);

/**
 * Parse and handle an incoming message on the WebSocket connection.
 * @param {string} message - the message received from the WebSocket
 */
ws.onmessage = function (message) {
    const msg = JSON.parse(message.data);
    switch (msg["type"]) {
        case "viz_state":
            // Update visualization state
            controller.render(msg["data"])
            break;
        case "end":
            // We have reached the end of the model
            controller.done();
            break;
        case "model_params":
            // Create GUI elements for each model parameter and reset everything
            initGUI(msg["params"]);
            controller.reset();
            break;
        default:
            // There shouldn't be any other message
            console.log("Unexpected message.");
            console.log(msg);
    }
};

/**
 * Turn an object into a string to send to the server, and send it.
 * @param {string} message - The message to send to the Python server
 */
const send = function (message) {
    const msg = JSON.stringify(message);
    ws.send(msg);
};


/*
 * GUI initialization (for input parameters)
 */

/**
 * Create the GUI with user-settable parameters
 * @param {object} model_params - Create the GUI from these model parameters
 */
const initGUI = function (model_params) {

    const sidebar = $("#sidebar");

    var onSubmitCallback = function (param_name, value) {
        send({ "type": "submit_params", "param": param_name, "value": value });
    };

    var addBooleanInput = function (param, obj) {
        var domID = param + '_id';
        sidebar.append([
            "<div class='input-group input-group-lg'>",
            "<p><label for='" + domID + "' class='label label-primary'>" + obj.name + "</label></p>",
            "<input class='model-parameter' id='" + domID + "' type='checkbox'/>",
            "</div>"
        ].join(''));
        $('#' + domID).bootstrapSwitch({
            'state': obj.value,
            'size': 'small',
            'onSwitchChange': function (e, state) {
                onSubmitCallback(param, state);
            }
        });
    };

    var addNumberInput = function (param, obj) {
        var domID = param + '_id';
        sidebar.append([
            "<div class='input-group input-group-lg'>",
            "<p><label for='" + domID + "' class='label label-primary'>" + obj.name + "</label></p>",
            "<input class='model-parameter' id='" + domID + "' type='number'/>",
            "</div>"
        ].join(''));
        var numberInput = $('#' + domID);
        numberInput.val(obj.value);
        numberInput.on('change', function () {
            onSubmitCallback(param, Number($(this).val()));
        })
    };

    var addSliderInput = function (param, obj) {
        var domID = param + '_id';
        var tooltipID = domID + "_tooltip";
        sidebar.append([
            "<div class='input-group input-group-lg'>",
            "<p>",
            "<a id='" + tooltipID + "' data-toggle='tooltip' data-placement='top' class='label label-primary'>",
            obj.name,
            "</a>",
            "</p>",
            "<input id='" + domID + "' type='text' />",
            "</div>"
        ].join(''));

        // Enable tooltip label
        if (obj.description !== null) {
            $(tooltipID).tooltip({
                title: obj.description,
                placement: 'right'
            });
        }

        // Setup slider
        var sliderInput = $("#" + domID);
        sliderInput.slider({
            min: obj.min_value,
            max: obj.max_value,
            value: obj.value,
            step: obj.step,
            ticks: [obj.min_value, obj.max_value],
            ticks_labels: [obj.min_value, obj.max_value],
            ticks_positions: [0, 100]
        });
        sliderInput.on('change', function () {
            onSubmitCallback(param, Number($(this).val()));
        })
    };

    var addChoiceInput = function (param, obj) {
        var domID = param + '_id';
        var span = "<span class='caret'></span>";
        var template = [
            "<p><label for='" + domID + "' class='label label-primary'>" + obj.name + "</label></p>",
            "<div class='dropdown'>",
            "<button id='" + domID + "' class='btn btn-default dropdown-toggle' type='button' data-toggle='dropdown'>" +
            obj.value + " " + span,
            "</button>",
            "<ul class='dropdown-menu' role='menu' aria-labelledby='" + domID + "'>"
        ];
        var choiceIdentifiers = [];
        for (var i = 0; i < obj.choices.length; i++) {
            var choiceID = domID + '_choice_' + i;
            choiceIdentifiers.push(choiceID);
            template.push(
                "<li role='presentation'><a class='pick-choice' id='" + choiceID + "' role='menuitem' tabindex='-1' href='#'>",
                obj.choices[i],
                "</a></li>"
            );
        }

        // Close the dropdown options
        template.push("</ul>", "</div>");

        // Finally render the dropdown and activate choice listeners
        sidebar.append(template.join(''));
        choiceIdentifiers.forEach(function (id, idx) {
            $('#' + id).on('click', function () {
                var value = obj.choices[idx];
                $('#' + domID).html(value + ' ' + span);
                onSubmitCallback(param, value);
            });
        });
    };

    var addTextBox = function (param, obj) {
        var well = $('<div class="well">' + obj.value + '</div>')[0];
        sidebar.append(well);
    };

    var addParamInput = function (param, option) {
        switch (option['param_type']) {
            case 'checkbox':
                addBooleanInput(param, option);
                break;

            case 'slider':
                addSliderInput(param, option);
                break;

            case 'choice':
                addChoiceInput(param, option);
                break;

            case 'number':
                addNumberInput(param, option);   // Behaves the same as just a simple number
                break;

            case 'static_text':
                addTextBox(param, option);
                break;
        }
    };

    for (var option in model_params) {

        var type = typeof (model_params[option]);
        var param_str = String(option);

        switch (type) {
            case "boolean":
                addBooleanInput(param_str, { 'value': model_params[option], 'name': param_str });
                break;
            case "number":
                addNumberInput(param_str, { 'value': model_params[option], 'name': param_str });
                break;
            case "object":
                addParamInput(param_str, model_params[option]);    // catch-all for params that use Option class
                break;
        }
    }
};

// Backward-Compatibility aliases
const control = controller;
const elements = vizElements;
