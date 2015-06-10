
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

// Prepares "Create Rule" modal for POST request.
// Note: I'm going to pretend I didn't write this function. T_T
function postCreateRuleForm() {
    var save_id = "#save-rule-button";
    //var form_id = "#create-rule-form";
    //var modal_id = "#create-rule-modal";
    var post_url= "/create-rule";
    var redirect_url= document.location.href;

    $(save_id).click(function(e) {
        var caller_number = $("#form-caller-number").val();
        var condition = $("input[name='radio-condition']:checked").attr("id");

        if (condition == "form-call-condition-always") {
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
        } else if (condition == "form-call-condition-time") {
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
        }
    });
}

function main() {
    bindToggleToCreateRuleCondition();
    addNewBusyTimeRows();
    postCreateRuleForm();
};

main();
