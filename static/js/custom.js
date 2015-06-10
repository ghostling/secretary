/**
 * form-call-condition-always, radio-condition
 *   condition-always-subform
 * form-call-condition-time, radio-condition
 *   condition-time-subform
 */

function main() {
    // Toggle visibility of subforms for "always"/"time based" conditions
    // of a rule.
    $("input[name='radio-condition']").click(function() {
        $("#condition-always-sub-form").toggle()
        $("#condition-time-sub-form").toggle()
    });

    // "+" Button: Add more rows under "Busy times"
    $("#button-add-busy-time").click(function(e) {
        e.preventDefault();
        $("<div>").addClass("uk-grid uk-grid-small")
                .append($("<div>").addClass("uk-width-1-3 uk-form-icon")
                    .append($("<input type=\"text\" placeholder=\"Start time\" data-uk-timepicker>")))
                .append($("<div>").addClass("uk-width-1-3 uk-form-icon")
                    .append($("<input type=\"text\" placeholder=\"End time\" data-uk-timepicker>")))
                .append($("<div>").addClass("uk-width-1-3")
                    .append($("<input type=\"text\" placeholder=\"Label\">")))
                .appendTo($("#form-busy-times"));
    });
};

main();
