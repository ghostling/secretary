
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

function bindCreateAlwaysRule() {
    var redirect_url= document.location.href;
    $("#condition-always-form").submit(function (e) {
        e.preventDefault();
        var caller_number = $("#form-caller-number").val();
        var action = $("input[name='radio-always-action']:checked").attr("id");

        if (action == "form-always-forward") {
            // Do stuff
        } else if (action == "form-always-play") {
            // What to play
            var play_type = $("#form-always-play-type :selected").attr("id");
            if (play_type == "form-always-play-text") {
                var text_to_play = $("#form-always-play-data").val();
            } else if (play_type == "form-always-play-audio") {
                // TODO: Implement later.
            }

            // Take message or not
            if ($("#form-always-take-message").is(":checked")) {
                // Take Message
            } else {
                // No
            }
        }
    });
};

function bindCreateTimeRule() {
    var redirect_url= document.location.href;
    $("#condition-time-form").submit(function (e) {
        e.preventDefault();
        var caller_number = $("#form-caller-number").val();

        // Get busy times
        var busy_entries = $(".busy-time-entry");
        var num_busy_entries = busy_entries.length;
        for (var i = 0; i < num_busy_entries; i++) {
            var start_time = $(busy_entries[i]).find(".start-time").val();
            var end_time = $(busy_entries[i]).find(".end-time").val();
            var label = $(busy_entries[i]).find(".label").val();
        }

        // Get busy rules
        if ($("#form-time-busy-play").is(":checked")) {
            // What to play
            var play_type = $("#form-time-busy-play-type :selected").attr("id");
            if (play_type == "form-time-busy-play-text") {
                var text_to_play = $("#form-time-busy-play-data").val();
            } else if (play_type == "#form-time-busy-play-audio") {
                // TODO: Implement later.
            }
        }
        if ($("#form-time-busy-take-message").is(":checked")) {
            // Take message
        }
    });
};

function main() {
    bindToggleToCreateRuleCondition();
    addNewBusyTimeRows();
    //postCreateRuleForm();
    bindCreateAlwaysRule();
    bindCreateTimeRule();
};

main();
