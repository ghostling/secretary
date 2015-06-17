import os
import json

from datetime import datetime
from flask import Flask, Response, request, render_template, url_for, make_response, redirect, session
from firebase import firebase
from pytz import timezone
from twilio import twiml
from twilio.rest import TwilioRestClient

from testdata import TEST_RULES

# Pull in configuration from system environment variables
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
FIREBASE_SECRET = os.environ.get("FIREBASE_SECRET")

# Create an authenticated client to make requests to Twilio.
# client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Connect to Firebase
fb = firebase.FirebaseApplication("https://twilio-secretary.firebaseio.com", None)

# Timezone of user (Twilio number owner).
USER_TIMEZONE = timezone('US/Pacific')
USER_REAL_NUMBER = fb.get("/personal-number", None)

app = Flask(__name__)
app.config["SECRET_KEY"] = TWILIO_AUTH_TOKEN

@app.route("/", methods=["GET"])
def index():
    if session.get("account_sid"):
        sid = session.get("account_sid")
        twilio_number = fb.get("/"+sid+"/twilio-number", None)
        real_number = fb.get("/"+sid+"/real-number", None)
        session["twilio_number"] = twilio_number
        session["real_number"] = real_number
        rules = fb.get("/"+sid+"/rules", None)

        return render_template("index.html",
                twilioNumber=twilio_number,
                realNumber=real_number,
                rules=rules)
    else:
        return render_template("index.html",
                newUser=True)

@app.route("/update-numbers", methods=["POST"])
def update_numbers():
    twilio_number = request.form["twilio_number"]
    real_number = request.form["real_number"]
    fb.put("/"+session.get("account_sid"), "twilio-number", twilio_number)
    fb.put("/"+session.get("account_sid"), "real-number", real_number)
    return make_response('', 200)


@app.route("/twilio-connect", methods=["GET","POST"])
def twilio_connect():
    sid = request.values.get("AccountSid", None)
    client = TwilioRestClient(sid, TWILIO_AUTH_TOKEN)
    acc_sid = client.accounts.list()[0].sid
    session["account_sid"] = acc_sid

    if not fb.get("/" + sid, None):
        fb.put("/", sid, {"acc_sid": session["account_sid"]})

    return redirect(url_for("index"))

@app.route("/twilio-disconnect", methods=["GET","POST"])
def twilio_disconnect():
    account_to_delete = request.values.get("AccountSid", None)
    fb.delete("/"+account_to_delete, None)
    session.pop("account_sid", None)
    return redirect(url_for("index"))

@app.route("/secretary/<int:sec_number>", methods=["POST","GET"])
def secretary(sec_number):
    """ The core of the application. Handles a phone call through Twilio and
        responds to it appropriately by predefined rules for the specific
        caller or all other callers. """
    acc_sid = request.values.get("AccountSid")

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
                resp.say("I am currently " + interval.get("label"))
                break
        if not busy:
            resp.dial(USER_REAL_NUMBER)

    if caller_rule.get("take_message"):
        resp.say("Leave a message after the tone. Please press pound \
                when you're done.")
        resp.record(playBeep=True, maxLength="90", finishOnKey="#", action="/handle-recording")
    return str(resp)

@app.route("/handle-recording", methods=["POST"])
def handle_recording():
    resp = twiml.Response()
    resp.say("Thanks for the message. I'll get back to you later. Good bye.")
    return str(resp)

def is_time_in_interval(interval):
    current_local_time = datetime.now(USER_TIMEZONE)
    now_time = datetime.strptime(
            current_local_time.strftime("%X"), "%X")
    start_time = datetime.strptime(interval.get("start"), "%H:%M")
    end_time = datetime.strptime(interval.get("end"), "%H:%M")
    print now_time, start_time, end_time

    return start_time <= now_time and now_time <= end_time

def get_rule_for_call(request):
    acc_sid = request.values.get("AccountSid")
    from_number = request.values.get("From", None)[2:]
    caller_rule = fb.get("/"+acc_sid+"/rules/"+from_number, None)
    if caller_rule and caller_rule.get("is_active"):
        return caller_rule
    return fb.get("/"+acc_sid+"/rules/*", None) # The everyone else rule.

def create_response(response_rules, resp):
    """ Plays a specified mp3 if our response should be audio, otherwise, let
        the robot voice speak some text. """
    if response_rules.get("type") == "text":
        resp.say(response_rules.get("data"))
    elif response_rules.get("type") == "audio":
        resp.say("An audio message should play later.")
    return resp

@app.route("/create-rule", methods=["POST"])
def create_rule():
    rule = eval(request.form.keys()[0])
    number = rule.keys()[0]
    fb.put("/"+session["account_sid"]+"/rules", number, rule[number])
    return make_response('', 200)

@app.route("/enable-rule", methods=["POST"])
def enable_rule():
    number = request.form["number"]
    fb.put("/"+session["account_sid"]+"/rules/"+number, "is_active", 1)
    return make_response('', 200)

@app.route("/disable-rule", methods=["POST"])
def disable_rule():
    number = request.form["number"]
    fb.put("/"+session["account_sid"]+"/rules/"+number, "is_active", 0)
    return make_response('', 200)

if __name__ == "__main__":
    app.run(debug=True)
