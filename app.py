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

@app.route('/', methods=['GET'])
def main():
    return "Hello World"

@app.route('/secretary', methods=['POST'])
def secretary():
    resp = twiml.Response()
    resp.say('Hello monkey')
    print request.values.get('From', None)
    return str(resp)

if __name__ == '__main__':
    app.run()
