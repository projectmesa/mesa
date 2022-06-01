import Slider from 'bootstrap-slider'
import $ from 'jquery'

export const initGUI = function (model_params, send) {
    const sidebar = $("#sidebar");

    const onSubmitCallback = function (param_name, value) {
        send({ type: "submit_params", param: param_name, value: value });
    };

    const addBooleanInput = function (param, obj) {
        const domID = param + "_id";
        sidebar.append(
            [
                "<div>",
                "<p><label for='" +
                domID +
                "' class='badge badge-primary'>" +
                obj.name +
                "</label></p>",
                "<input class='model-parameter' id='" + domID + "' type='checkbox'/>",
                "</div>",
            ].join("")
        );
        $("#" + domID).bootstrapSwitch({
            state: obj.value,
            size: "small",
            onSwitchChange: function (e, state) {
                onSubmitCallback(param, state);
            },
        });
    };

    const addNumberInput = function (param, obj) {
        const domID = param + "_id";
        sidebar.append(
            [
                "<div>",
                "<p><label for='" +
                domID +
                "' class='badge badge-primary'>" +
                obj.name +
                "</label></p>",
                "<input class='model-parameter' id='" + domID + "' type='number'/>",
                "</div>",
            ].join("")
        );
        const numberInput = $("#" + domID);
        numberInput.val(obj.value);
        numberInput.on("change", function () {
            onSubmitCallback(param, Number($(this).val()));
        });
    };

    const addSliderInput = function (param, obj) {
        const domID = param + "_id";
        const tooltipID = domID + "_tooltip";
        let tooltip = "";
        // Enable tooltip label
        if (obj.description !== null) {
            tooltip = `title='${obj.description}'`;
        }

        sidebar.append(
            [
                "<div>",
                "<p>",
                `<a id='${tooltipID}' ${tooltip} data-toggle='tooltip' data-placement='top' class='badge badge-primary'>`,
                obj.name,
                "</a>",
                "</p>",
                "<input id='" + domID + "' type='text' />",
                "</div>",
            ].join("")
        );

        // Setup slider
        const sliderInput = new Slider(`#${domID}`, {
            min: obj.min_value,
            max: obj.max_value,
            value: obj.value,
            step: obj.step,
            ticks: [obj.min_value, obj.max_value],
            ticks_labels: [obj.min_value, obj.max_value],
            ticks_positions: [0, 100],
        });
        sliderInput.on("change", function () {
            onSubmitCallback(param, Number($(this).val()));
        });
    };

    const addChoiceInput = function (param, obj) {
        const domID = param + "_id";
        const span = "<span class='caret'></span>";
        const template = [
            "<p><label for='" +
            domID +
            "' class='badge badge-primary'>" +
            obj.name +
            "</label></p>",
            "<div class='dropdown'>",
            "<button id='" +
            domID +
            "' class='btn btn-default dropdown-toggle' type='button' data-toggle='dropdown'>" +
            obj.value +
            " " +
            span,
            "</button>",
            "<ul class='dropdown-menu' role='menu' aria-labelledby='" + domID + "'>",
        ];
        const choiceIdentifiers = [];
        for (let i = 0; i < obj.choices.length; i++) {
            const choiceID = domID + "_choice_" + i;
            choiceIdentifiers.push(choiceID);
            template.push(
                "<li role='presentation'><a class='pick-choice' id='" +
                choiceID +
                "' role='menuitem' tabindex='-1' href='#'>",
                obj.choices[i],
                "</a></li>"
            );
        }

        // Close the dropdown options
        template.push("</ul>", "</div>");

        // Finally render the dropdown and activate choice listeners
        sidebar.append(template.join(""));
        choiceIdentifiers.forEach(function (id, idx) {
            $("#" + id).on("click", function () {
                const value = obj.choices[idx];
                $("#" + domID).html(value + " " + span);
                onSubmitCallback(param, value);
            });
        });
    };

    const addTextBox = function (param, obj) {
        const well = $('<div class="well">' + obj.value + "</div>")[0];
        sidebar.append(well);
    };

    const addParamInput = function (param, option) {
        switch (option["param_type"]) {
            case "checkbox":
                addBooleanInput(param, option);
                break;

            case "slider":
                addSliderInput(param, option);
                break;

            case "choice":
                addChoiceInput(param, option);
                break;

            case "number":
                addNumberInput(param, option); // Behaves the same as just a simple number
                break;

            case "static_text":
                addTextBox(param, option);
                break;
        }
    };

    for (const option in model_params) {
        const type = typeof model_params[option];
        const param_str = String(option);

        switch (type) {
            case "boolean":
                addBooleanInput(param_str, {
                    value: model_params[option],
                    name: param_str,
                });
                break;
            case "number":
                addNumberInput(param_str, {
                    value: model_params[option],
                    name: param_str,
                });
                break;
            case "object":
                addParamInput(param_str, model_params[option]); // catch-all for params that use Option class
                break;
        }
    }
};