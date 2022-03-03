# Import modules
import json
import re
import paho.mqtt.client as mqtt
import time
import requests

# MQTT Channel details. Check Rhasspy Documentation for this
_SUB_ON_HOTWORD            = 'hermes/hotword/+/detected'
_SUB_ON_SAY                = 'hermes/tts/say'
_SUB_ON_THINK              = 'hermes/asr/textCaptured'
_SUB_ON_LISTENING          = 'hermes/asr/startListening'
_SUB_LEDS_ON_ERROR         = 'hermes/nlu/intentNotRecognized'
_SUB_INTENT_ON_SUCCESS     = 'hermes/nlu/intentParsed'
_SUB_ON_PLAY_FINISHED      = 'hermes/audioServer/{}/playFinished'
_SUB_ON_TTS_FINISHED       = 'hermes/tts/sayFinished'
_SUB_ON_INTENT             = 'hermes/intent/#'

# Hotword regex extract
_hotwordRegex = re.compile(_SUB_ON_HOTWORD.replace('+', '(.*)'))

def on_connect(client, userdata, flags, rc):
    """
        Called when connected to MQTT broker.
    """
    client.subscribe([
        (_SUB_ON_HOTWORD, 0),
        (_SUB_ON_SAY, 0),
        (_SUB_ON_THINK, 0),
        (_SUB_ON_LISTENING, 0),
        (_SUB_ON_PLAY_FINISHED, 0),
        (_SUB_ON_TTS_FINISHED, 0),
        (_SUB_LEDS_ON_ERROR, 0),
        (_SUB_INTENT_ON_SUCCESS, 0),
        (_SUB_ON_INTENT, 0),
    ])
    print("Connected. Waiting for intents.")


def on_disconnect(client, userdata, flags, rc):
    """
        Called when disconnected from MQTT broker.
    """
    client.reconnect()

def on_message(client, userdata, msg):
    """
        Called each time a message is received on a subscribed topic.
    """
    # Get NLU payload
    nlu_payload = json.loads(msg.payload)
    # print("-----------------------------")
    # print(msg.topic)
    # print(nlu_payload)

    # Side_id of aivoicebox instance
    site_id = nlu_payload["siteId"]
    
    # Run only when intent is successfully detected
    if msg.topic == _SUB_INTENT_ON_SUCCESS:
        time.sleep(1)

        # Detected intent name
        intent = nlu_payload["intent"]["intentName"]

        # Run logic for detected Weather intent 
        if intent == "Tweet":

            # User spoken input sentence
            sentence = nlu_payload["input"]

            # City name detected
            tweet_text = nlu_payload["slots"][0]["rawValue"]

            print(tweet_text)
        
            # publish text to speaker
            # client.publish("hermes/tts/say", json.dumps({"text": sentence, "siteId": site_id}))

# Create MQTT client and connect to broker
client = None

# AiVoiceBox init
try:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect("localhost", 12183)

    while not client.is_connected():
        client.loop()
        print(client.is_connected())
except:
    print("client is not connected")

client.loop_forever()
