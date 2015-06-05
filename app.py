import os

from datetime import datetime
from flask import Flask, Response, request, render_template
from pytz import timezone
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

# Timezone of user (Twilio number owner).
USER_TIMEZONE = timezone('US/Pacific')

# Create an authenticated client to make requests to Twilio.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)

# Dummy test data.
# TODO: Move.
rules = {
    "+14134062242": {
        "condition": "always",
        "response": {
            "type": "text",
            "data": "Hello"
            },
        "take_message": 1
        },
    "+19193608390": {
        "condition": "time",
        "busy_intervals": [
            { "label": "work",
                "start": "09:00:00",
                "end": "17:00:00"},
            { "label": "sleep",
                "start": "24:00:00",
                "end": "08:00:00"},
            ],
        "response": {
            "type": "audio",
            "data": "static/audio/recording.mp3"
            },
        "take_message": 0
        },
    "*": {
        "condition": "always",
        "response": {
            "type": "audio",
            "data": "static/audio/test.mp3"
            },
        "take_message": 0
        },
}


@app.route("/", methods=["GET"])
def main():
    # TODO: All the frontend dashboard stuff.
    return "Hello World"

@app.route("/secretary", methods=["POST"])
def secretary():
    """ The core of the application. Handles a phone call through Twilio and
        responds to it appropriately by predefined rules for the specific
        caller or all other callers. """

    resp = twiml.Response()

    caller_rule = get_rule_for_call(request)

    if caller_rule["condition"] == "always":
        resp = create_response(caller_rule["response"], resp)
    elif caller_rule["condition"] == "time":
        for interval in caller_rule["busy_intervals"]:
            if is_time_in_interval(interval):
                resp.say("I am currently " + interval["label"])
            else:
                resp.dial("+19193608311")

    if caller_rule["take_message"]:
        resp.say("Leave a message after the tone. Please press pound
                when you're done.")
        resp.record(playBeep=True, maxLength="90", finishOnKey="#")
    return str(resp)

def is_time_in_interval(interval):
    current_local_time = datetime.now(USER_TIMEZONE)
    standardized_time = datetime.strptime(
            current_local_time.strftime("%X"), "%X")
    start_time = datetime.strptime(interval["start"], "%X")
    end_time = datetime.strptime(interval["end"], "%X")

    return start <= t and t <= end

def get_rule_for_call(request):
    from_number = request.values.get("From", None)
    caller_rule = {}
    # Load the rule to execute for this caller.
    if from_number in rules:
        caller_rule = rules[from_number]
    else:
        caller_rule = rules["*"] # The everyone else rule.
    return caller_rule

def create_response(response_rules, resp):
    """ Plays a specified mp3 if our response should be audio, otherwise, let
        the robot voice speak some text. """
    print response_rules
    if response_rules["type"] == "text":
        resp.say(response_rules["data"])
    elif response_rules["type"] == "audio":
        resp.play("http://7cfc6ecc.ngrok.io/"+response_rules["data"])
    print str(resp)
    return resp


@app.route("/handle-recording", methods=["GET", "POST"])
def handle_recording():
    """ Takes the voicemail and saves it somewhere so that the boss can listen
        to it if she pleases. """
    recording_url = request.values.get("RecordingUrl", None)
    # TODO: Save and add this recording somewhere like a dashboard.

if __name__ == "__main__":
    app.run()
