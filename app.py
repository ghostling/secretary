import os

from flask import Flask, Response, request, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Flask
app = Flask(__name__)


rules = {
    '+9193608320': {
        'condition': 'always',
        'response': {
            'type': 'string',
            'data': 'You have reached Jessie, but she is currently unavailable. Please call back later or leave a message'
            }
        'take_message': 1
        },
    '+9193608390': {
        'condition': 'time',
        'response': {
            'type': 'audio',
            'data': 'static/audio/recording.mp3'
            }
        'take_message': 0
        },
}


@app.route('/', methods=['GET'])
def main():
    # TODO: All the frontend dashboard stuff.
    return "Hello World"

@app.route('/secretary', methods=['POST'])
def secretary():
    """ The core of the application. Handles a phone call through Twilio and
        responds to it appropriately by predefined rules for the specific
        caller or all other callers. """
    resp = twiml.Response()
    from_number = request.values.get('From', None)

    # Load the rule to execute for this caller.
    if from_number in rules:
        caller_rule = rules[from_number]
    else:
        caller_rule = rules['*'] # The everyone else rule.

    if caller_rule['condition'] == 'always':
        resp = create_response(caller_rule['response'], resp)
    elif caller_rule['condition'] == 'time':
        # TODO: Figure out how the time condition will work.
        pass

    if caller_rule['take_message']:
        resp.say('Leave a message after the tone.')
        resp.record(maxLength='90', action='/handle-recording')

    resp.say('Hello monkey')
    return str(resp)

def create_response(response_rules, resp):
    """ Plays a specified mp3 if our response should be audio, otherwise, let
        the robot voice speak some text. """
    if response_rules['type'] == 'text':
        resp.say(response_rules['data'])
    elif response_rules['type'] == 'data':
        resp.play(response_rules['data'])
    return resp


@app.route('/handle-recording', methods=['GET', 'POST'])
def handle_recording():
    """ Takes the voicemail and saves it somewhere so that the boss can listen
        to it if she pleases. """
    recording_url = request.values.get("RecordingUrl", None)
    # TODO: Save and add this recording somewhere like a dashboard.

if __name__ == '__main__':
    app.run()
