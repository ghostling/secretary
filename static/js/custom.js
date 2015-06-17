
// Toggle visibility of subforms for "always"/"time based" conditions
// of a rule.
function bindToggleToCreateRuleCondition() {
    $("input[name='radio-condition']").click(function() {
        $("#condition-always-sub-form").toggle()
        $("#condition-time-sub-form").toggle()
    });
};

// "+" Button: Add more rows under "Busy times"
// TODO: Make this nicer...later.
function addNewBusyTimeRows() {
    $("#button-add-busy-time").click(function(e) {
        e.preventDefault();
        $("<div>").addClass("busy-time-entry uk-grid uk-grid-small")
                .append($("<div>").addClass("uk-width-1-3 uk-form-icon")
                    .append($("<input type=\"text\" placeholder=\"Start time\" class=\"start-time\" data-uk-timepicker>")))
                .append($("<div>").addClass("uk-width-1-3 uk-form-icon")
                    .append($("<input type=\"text\" placeholder=\"End time\" class=\"end-time\" data-uk-timepicker>")))
                .append($("<div>").addClass("uk-width-1-3")
                    .append($("<input type=\"text\" placeholder=\"Label\" class=\"label\">")))
                .appendTo($("#form-busy-times"));
    });
};

function sendNewRuleToFlask(json_data) {
    $.ajax({
        type: "POST",
        url: "/create-rule",
        data: json_data,
        complete: function() {
            location.reload();
        },
    });
};

// Parsing and handling for the "always" rule form.
function bindCreateAlwaysRule() {
    var redirect_url= document.location.href;

    $("#condition-always-form").submit(function (e) {
        e.preventDefault();
        var always_rule = {"condition": "always"};
        var caller_number = $("#form-caller-number").val();
        var action = $("input[name='radio-always-action']:checked").attr("id");

        if (action == "form-always-forward") {
            always_rule.forward = 1;
        } else if (action == "form-always-play") {
            var text_to_play = $("#always-data-text").val();
            always_rule.response = { "data" : text_to_play, "type" : "text" };
            // What to play
            /*
            var play_type = $("#form-always-play-type :selected").attr("id");
            if (play_type == "form-always-play-text") {
                var text_to_play = $("#always-data-text").val();
                always_rule.response = { "data" : text_to_play, "type" : "text" };
            } else if (play_type == "form-always-play-audio") {
                // TODO: Actually make this work.
                var selectedMp3 = $("#always-upload-select")[0].files[0];
                always_rule.response = { "data" : selectedMp3, "type" : "audio" };
            }
            */

            // Take message or not
            if ($("#form-always-take-message").is(":checked")) {
                always_rule.take_message = 1;
            } else {
                always_rule.take_message = 0;
            }
        }

        always_rule.is_active = 1;

        // Assigns rule to specified caller number.
        complete_rule = {};
        complete_rule[caller_number] = always_rule;
        always_rule_json = JSON.stringify(complete_rule);
        sendNewRuleToFlask(always_rule_json);
    });
};

// Parsing and handling for the "time" rule form.
function bindCreateTimeRule() {
    var redirect_url= document.location.href;
    $("#condition-time-form").submit(function (e) {
        e.preventDefault();
        var time_rule = {"condition": "time"};
        var caller_number = $("#form-caller-number").val();

        // Get busy times
        var busy_entries = $(".busy-time-entry");
        var num_busy_entries = busy_entries.length;
        time_rule.busy_intervals = {};
        for (var i = 0; i < num_busy_entries; i++) {
            var start_time = $(busy_entries[i]).find(".start-time").val();
            var end_time = $(busy_entries[i]).find(".end-time").val();
            var label = $(busy_entries[i]).find(".label").val();
            if (start_time != "" && end_time != "" && label != "") {
                time_rule.busy_intervals[i] = {
                    "start": start_time,
                    "end": end_time,
                    "label": label
                };
            }
        }

        // Get busy rules
        /*
        if ($("#form-time-busy-play").is(":checked")) {
            // What to play
            var play_type = $("#form-time-busy-play-type :selected").attr("id");
            if (play_type == "form-time-busy-play-text") {
                var text_to_play = $("#time-data-text").val();
                time_rule.response = { "data" : text_to_play, "type" : "text" };
            } else if (play_type == "#form-time-busy-play-audio") {
                // TODO: Actually make this work.
                var selectedMp3 = $("#time-upload-select")[0].files[0];
                always_rule.response = { "data" : selectedMp3, "type" : "audio" };
            }
        }
        */

        // Take message or not
        if ($("#form-time-busy-take-message").is(":checked")) {
            time_rule.take_message = 1;
        } else {
            time_rule.take_message = 0;
        }

        time_rule.is_active = 1;

        // Assigns rule to specified caller number.
        complete_rule = {};
        complete_rule[caller_number] = time_rule;
        time_rule_json = JSON.stringify(complete_rule);
        sendNewRuleToFlask(time_rule_json);
    });
};

// Toggling the "Active" checkbox next to a rule will change its state.
function toggleNumberActiveState() {
    $(".rule-is-active").change( function() {
        if ($(this).is(":checked")) {
            var number = $(this)[0].dataset.number;
            $.ajax({
                type: "POST",
                url: "/enable-rule",
                data: {number:number},
                complete: function() {
                },
    });
        } else {
            var number = $(this)[0].dataset.number;
            $.ajax({
                type: "POST",
                url: "/disable-rule",
                data: {number:number},
                complete: function() {
                },
            });
        }
    });
};

function toggleDataInput() {
    $("#form-always-play-type").change(function() {
        var play_type = $("#form-always-play-type :selected").attr("id");
        if (play_type == "form-always-play-text") {
            $("#always-data-text").removeClass("uk-hidden");
            $("#always-data-audio").addClass("uk-hidden");
        } else {
            $("#always-data-audio").removeClass("uk-hidden");
            $("#always-data-text").addClass("uk-hidden");
        }
    });

    $("#form-time-busy-play-type").change(function() {
        var play_type = $("#form-time-busy-play-type :selected").attr("id");
        if (play_type == "form-time-busy-play-text") {
            $("#time-data-text").removeClass("uk-hidden");
            $("#time-data-audio").addClass("uk-hidden");
        } else {
            $("#time-data-audio").removeClass("uk-hidden");
            $("#time-data-text").addClass("uk-hidden");
        }
    });
};

function main() {
    bindToggleToCreateRuleCondition();
    addNewBusyTimeRows();
    bindCreateAlwaysRule();
    bindCreateTimeRule();
    toggleNumberActiveState();

    toggleDataInput();
};

main();
