# Dummy test data.
TEST_RULES = {
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
