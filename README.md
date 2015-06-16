# Secretary
You're such a busy, important, fancy-schmancy person. You don't have time to
answer phone calls or pick up your phone at all because you're so important.
Well, let Secretary take care of all your needs. It will take all your calls
and decide who is worthy of your time. It will also allow you to give certain
people more personal messages before they are prompted with a rude beeeeep. And
most importantly, it will help you fend off creeps by just always giving
someone the "voicemail."

Or you're like me, and mom won't stop calling you during lectures and work, and
you're tired of picking up to tell her you're not dead and are actually working.

## How-To Use
Make sure you have a valid Twilio account & number as well as a Firebase account. You'll need to first configure your system env variables as referenced in app.py with all of your information. Then you can run by simply typing:
```
> python app.py
...
> ngrok http 5000
```
Or whatever port number. And then put the ngrok link in your Twilio Number setup. Now you can add rules from the Flask app and call your Twilio Number to utilize your own personal secretary!
