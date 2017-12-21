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
    this.done = false;
    this.fps = 3; // Frames per second
};

var player; // Variable to store the continuous player
var control = new MesaVisualizationControl();
var elements = [];  // List of Element objects
var model_params = {};
var reporters = [];

// Playback buttons
var playPauseButton = $('#play-pause');
var stepButton = $('#step');
var resetButton = $('#reset');
var fpsControl = $('#fps').slider({
    max: 20,
    min: 0,
    value: 3,
    ticks: [0, 20],
    ticks_labels: [0, 20],
    ticks_position: [0, 100]
});

// Sidebar dom access
var sidebar = $("#sidebar");

// WebSocket Stuff
// Open the websocket connection; support TLS-specific URLs when appropriate

var ws = new WebSocket((window.location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");

ws.onopen = function() {
    console.log("Connection opened!");
    send({"type": "get_params"}); // Request model parameters when websocket is ready
    send({"type": "get_reporters"});
    reset();
};

// Add model parameters that can be edited prior to a model run
var initGUI = function() {

    var onSubmitCallback = function(param_name, value) {
        send({"type": "submit_params", "param": param_name, "value": value});
    };

    var addBooleanInput = function(param, obj) {
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
            'onSwitchChange': function(e, state) {
                onSubmitCallback(param, state);
            }
        });
    };

    var addNumberInput = function(param, obj) {
        var domID = param + '_id';
        sidebar.append([
            "<div class='input-group input-group-lg'>",
            "<p><label for='" + domID + "' class='label label-primary'>" + obj.name + "</label></p>",
            "<input class='model-parameter' id='" + domID + "' type='number'/>",
            "</div>"
        ].join(''));
        var numberInput = $('#' + domID);
        numberInput.val(obj.value);
        numberInput.on('change', function() {
            onSubmitCallback(param, Number($(this).val()));
        })
    };

    var addSliderInput = function(param, obj) {
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
        sliderInput.on('change', function() {
            onSubmitCallback(param, Number($(this).val()));
        })
    };

    var addChoiceInput = function(param, obj) {
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
        choiceIdentifiers.forEach(function (id) {
            $('#' + id).on('click', function () {
                var value = $(this).text();
                $('#' + domID).html(value + ' ' + span);
                onSubmitCallback(param, value);
            });
        });
    };

    var addTextBox = function(param, obj) {
        var well = $('<div class="well">' + obj.value + '</div>')[0];
        sidebar.append(well);
    };

    var addParamInput = function(param, option) {
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

        var type = typeof(model_params[option]);
        var param_str = String(option);

        switch (type) {
            case "boolean":
                addBooleanInput(param_str, {'value': model_params[option], 'name': param_str});
                break;
            case "number":
                addNumberInput(param_str, {'value': model_params[option], 'name': param_str});
                break;
            case "object":
                addParamInput(param_str, model_params[option]);    // catch-all for params that use Option class
                break;
        }
    }

    var addReporter = function(reporters) {

        sidebar.append(
          "<h3>Model Reporters</h3>"
        )

        var select = $("<select class='custom-select' id='reporter-selector'></select>")
        var option_selected = $("<option selected>Select reporter</option>")
        select.append(option_selected)
        for (var i =0; i < reporters.length; i++) {
          var option = $("<option value='" + i + "'>" + reporters[i] + "</option>")
          select.append(option)
        }
        sidebar.append(select)
    }


    addReporter(reporters)
    var chartButton = $('<button type="button" class="btn btn-secondary" onclick="createChart()">Create chart</button>')
    sidebar.append(chartButton)

    sortable(document.getElementById('elements'))
};

var createChart = function() {
    var e = $("#reporter-selector")[0];
    var label = e.options[e.selectedIndex].text;
    send({"type": "create_chart", "label": label})
    setTimeout(location.reload.bind(location), 100);
}

/** Parse and handle an incoming message on the WebSocket connection. */
ws.onmessage = function(message) {
    var msg = JSON.parse(message.data);
    console.log(msg)
    switch (msg["type"]) {
        case "viz_state":
            var data = msg["data"];
            for (var i in elements) {
                elements[i].render(data[i]);
            }
            console.log(data)
            break;
        case "end":
            // We have reached the end of the model
            control.running = false;
            control.done = true;
            console.log("Done!");
            clearInterval(player);
            $(playPauseButton.children()[0]).text("Done");
            break;
        case "model_params":
            console.log(msg["params"]);
            model_params = msg["params"];
            break;
        case "model_reporters":
            console.log(msg["reporters"])
            reporters = msg["reporters"]
            initGUI();
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
    control.done = false;
    if (!control.running)
        $(playPauseButton.children()[0]).text("Start");
};

/** Send a message to the server get the next visualization state. */
var single_step = function() {
    control.tick += 1;
    send({"type": "get_step", "step": control.tick});
};

/** Step the model forward. */
var step = function() {
    if (!control.running & !control.done) {single_step()}
    else if (!control.done) {run()};
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
    else if (!control.done) {
        control.running = true;
        player = setInterval(single_step, 1000/control.fps);
        anchor.text("Stop");
    }
};

var updateFPS = function() {
    control.fps = Number(fpsControl.val());
    if (control.running) {
        run();
        run();
    }
};

// Initilaize buttons on top bar
playPauseButton.on('click', run);
stepButton.on('click', step);
resetButton.on('click', reset);
fpsControl.on('change', updateFPS);

function sortable(rootEl) {
   var dragEl;
   var target

   // Making all siblings movable
   [].slice.call(rootEl.children).forEach(function (itemEl) {
       itemEl.draggable = true;
       itemEl.addEventListener('dragstart', onDragStart, false)
       itemEl.addEventListener('dragover', onDragOver, false);
       itemEl.addEventListener('dragend', onDragEnd, false);
       itemEl.addEventListener('dragenter', handleDragEnter, false);
       itemEl.addEventListener('dragleave', handleDragLeave, false);
   });

   function onDragStart(evt){
       dragEl = evt.target; // Remembering an element that will be moved

       // Limiting the movement type
       evt.dataTransfer.effectAllowed = 'move';
       evt.dataTransfer.setData('Text', dragEl.id);
   }

   // Function responsible for sorting
   function onDragOver(evt) {
       evt.preventDefault();
       evt.dataTransfer.dropEffect = 'move';
   }

   function handleDragEnter(e) {
     // this / e.target is the current hover target.
     this.classList.add('over');
     target = e.target
   }

   function handleDragLeave(e) {
     this.classList.remove('over');  // this / e.target is previous target element.
   }


   // End of sorting
   function onDragEnd(evt){
       evt.preventDefault();
       target.classList.remove('over');
       rootEl.insertBefore(dragEl, target)
   }
}
