import os
import json
from datetime import datetime
from flask import Flask, Response, request, render_template, url_for, make_response
from firebase import firebase
from pytz import timezone
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
FIREBASE_SECRET = os.environ.get("FIREBASE_SECRET")
FIREBASE_EMAIL = os.environ.get("FIREBASE_EMAIL")
FIREBASE_LINK = os.environ.get("FIREBASE_LINK")

# Create an authenticated client to make requests to Twilio.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Connect to Firebase
fb = firebase.FirebaseApplication(FIREBASE_LINK, None)
auth = firebase.FirebaseAuthentication(
        FIREBASE_SECRET, FIREBASE_EMAIL, debug=False, admin=True)
fb.authentication = auth

# Timezone of user (Twilio number owner).
USER_TIMEZONE = timezone('US/Pacific')
USER_REAL_NUMBER = fb.get("/personal-number", None)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """ This is the dashboard of the application. """
    rules = fb.get("/rules", None)
    return render_template("index.html",
            twilioNumber=TWILIO_NUMBER,
            personalNumber=USER_REAL_NUMBER,
            rules=rules)


@app.route("/secretary", methods=["POST"])
def secretary():
    """ The core of the application. Handles a phone call through Twilio and
        responds to it appropriately by predefined rules for the caller. """
    resp = twiml.Response()
    caller_rule = get_rule_for_call(request)

    if caller_rule.get("condition") == "always":
        if caller_rule.get("forward"):
            resp.dial(USER_REAL_NUMBER)
        else:
            resp = create_response(caller_rule.get("response"), resp)
    elif caller_rule.get("condition") == "time":
        busy = False
        for interval in caller_rule.get("busy_intervals"):
            if is_time_in_interval(interval):
                busy = True
                resp.say("Hello, you have reached Jessie's secretary. She is currently busy right now. "+interval.get("label"), voice="alice", language="en-AU")
                break
        if not busy:
            resp.dial(USER_REAL_NUMBER)

    if caller_rule.get("take_message"):
        resp.say("Leave a message after the tone. Please press pound \
                when you're done.", voice="alice", language="en-AU")
        resp.record(playBeep=True, maxLength="90", finishOnKey="#", action="/handle-recording/"+caller_rule.get("caller_name").replace(" ", ""))
    return str(resp)


@app.route("/handle-recording/<name>", methods=["POST"])
def handle_recording(name=None):
    resp = twiml.Response()
    resp.say("Thanks for the message. I'll let Jessie know you called.", voice="alice", language="en-AU")
    if name=="Everyoneelse":
        name = "Someone"
    message = client.messages.create(to=USER_REAL_NUMBER, from_=TWILIO_NUMBER, body="Secretary: "+name+" left you a voicemail.")
    return str(resp)


@app.route("/create-rule", methods=["POST"])
def create_rule():
    """ Creates a rule from the modal form. All data should be parsed before
        getting here. """
    rule = eval(request.form.keys()[0])
    number = rule.keys()[0]
    fb.put("/rules", number, rule[number])
    return make_response('', 200)


@app.route("/enable-rule", methods=["POST"])
def enable_rule():
    """ Handle enabling a disabled rule from dashboard. """
    number = request.form["number"]
    fb.put("/rules/"+number, "is_active", 1)
    return make_response('', 200)


@app.route("/disable-rule", methods=["POST"])
def disable_rule():
    """ Handle disabling an enabled rule from dashboard. """
    number = request.form["number"]
    fb.put("/rules/"+number, "is_active", 0)
    return make_response('', 200)


def is_time_in_interval(interval):
    """ Given an interval with a start and end time, figures out if the
        current time fits within the interval. """
    current_local_time = datetime.now(USER_TIMEZONE)
    now_time = datetime.strptime(
            current_local_time.strftime("%X"), "%X")
    start_time = datetime.strptime(interval.get("start"), "%H:%M")
    end_time = datetime.strptime(interval.get("end"), "%H:%M")

    return start_time <= now_time and now_time <= end_time


def get_rule_for_call(request):
    """ Uses the caller number in the request to see if a rule is set for
        this caller, if so, return the rule. """
    from_number = request.values.get("From", None)[2:]
    caller_rule = fb.get("/rules/"+from_number, None)
    if caller_rule and caller_rule.get("is_active"):
        return caller_rule
    return fb.get("/rules/*", None) # The everyone else rule.


def create_response(response_rules, resp):
    """ Plays a specified mp3 if our response should be audio, otherwise, let
        the robot voice speak some text. """
    if response_rules.get("type") == "text":
        resp.say(response_rules.get("data"), voice="alice", language="en-AU")
    elif response_rules.get("type") == "audio":
        # TODO: Implement.
        resp.say("An audio message should play later.", voice="alice", language="en-AU")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
