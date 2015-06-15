import os
import json

from datetime import datetime
from flask import Flask, Response, request, render_template, url_for, make_response
from firebase import firebase
from pytz import timezone
from twilio import twiml
from twilio.rest import TwilioRestClient

from testdata import TEST_RULES

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
FIREBASE_SECRET = os.environ.get("FIREBASE_SECRET")

# Create an authenticated client to make requests to Twilio.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Connect to Firebase
fb = firebase.FirebaseApplication("https://twilio-secretary.firebaseio.com", None)

# Timezone of user (Twilio number owner).
USER_TIMEZONE = timezone('US/Pacific')
USER_REAL_NUMBER = fb.get("/personal-number", None)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    rules = fb.get("/rules", None)

    return render_template("index.html",
            twilioNumber=TWILIO_NUMBER,
            personalNumber=USER_REAL_NUMBER,
            rules=rules)

@app.route("/secretary", methods=["POST"])
def secretary():
    """ The core of the application. Handles a phone call through Twilio and
        responds to it appropriately by predefined rules for the specific
        caller or all other callers. """

    resp = twiml.Response()

    caller_rule = get_rule_for_call(request)

    if caller_rule.get("condition") == "always":
        if caller_rule.get("forward"):
            resp.dial(USER_REAL_NUMBER)
        else:
            resp = create_response(caller_rule.get("response"), resp)
    elif caller_rule.get("condition") == "time":
        for interval in caller_rule.get("busy_intervals"):
            if is_time_in_interval(interval):
                resp.say("I am currently " + interval.get("label"))
            else:
                resp.dial(USER_REAL_NUMBER)

    if caller_rule.get("take_message"):
        resp.say("Leave a message after the tone. Please press pound \
                when you're done.")
        resp.record(playBeep=True, maxLength="90", finishOnKey="#")
    return str(resp)

def is_time_in_interval(interval):
    current_local_time = datetime.now(USER_TIMEZONE)
    standardized_time = datetime.strptime(
            current_local_time.strftime("%X"), "%X")
    start_time = datetime.strptime(interval.get("start"), "%X")
    end_time = datetime.strptime(interval.get("end"), "%X")

    return start <= t and t <= end

def get_rule_for_call(request):
    from_number = request.values.get("From", None)
    caller_rule = fb.get("/rules/"+from_number, None)

    if caller_rule:
        return caller_rule
    return fb.get("/rules/*", None) # The everyone else rule.

def create_response(response_rules, resp):
    """ Plays a specified mp3 if our response should be audio, otherwise, let
        the robot voice speak some text. """
    if response_rules.get("type") == "text":
        resp.say(response_rules.get("data"))
    elif response_rules.get("type") == "audio":
        resp.say("An audio message should play later.")
        #resp.play("http://7cfc6ecc.ngrok.io/"+response_rules["data"])
    return resp

@app.route("/create-rule", methods=["POST"])
def create_rule():
    rule = eval(request.form.keys()[0])
    number = rule.keys()[0]
    fb.put('/rules', number, rule[number])
    return make_response('', 200)

if __name__ == "__main__":
    app.run(debug=True)
