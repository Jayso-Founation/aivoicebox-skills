import json
import re
# pip install paho-mqtt
import paho.mqtt.client as mqtt
import pixels
import time

pixels = pixels.Pixels()

# MQTT Channel details. Check Rhasspy Documentation for this
_SUB_ON_HOTWORD            = 'hermes/hotword/+/detected'
_SUB_ON_SAY                = 'hermes/tts/say'
_SUB_ON_THINK              = 'hermes/asr/textCaptured'
_SUB_ON_LISTENING          = 'hermes/asr/startListening'
_SUB_LEDS_ON_ERROR         = 'hermes/nlu/intentNotRecognized'
_SUB_INTENT_ON_SUCCESS       = 'hermes/nlu/intentParsed'
_SUB_ON_PLAY_FINISHED      = 'hermes/audioServer/{}/playFinished'
_SUB_ON_TTS_FINISHED       = 'hermes/tts/sayFinished'
_SUB_ON_INTENT             = 'hermes/intent/#'


_hotwordRegex = re.compile(_SUB_ON_HOTWORD.replace('+', '(.*)'))

def setColor(color):
    for i in range(PIXELS_N):
        driver.set_pixel(i, color[0], color[1], color[2])
    driver.show()


def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
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
    """Called when disconnected from MQTT broker."""
    client.reconnect()


def on_message(client, userdata, msg):
    """Called each time a message is received on a subscribed topic."""
    nlu_payload = json.loads(msg.payload)
    # print("-----------------------------")
    # print(msg.topic)
    # print(nlu_payload)
    site_id = nlu_payload["siteId"]
    if msg.topic == _SUB_LEDS_ON_ERROR:
        
        sentence = "Try Again"
        # print("Recognition failure")
        # publish text to speaker
        client.publish("hermes/tts/say", json.dumps({"text": sentence, "siteId": site_id}))
    
    elif _hotwordRegex.match(msg.topic):
        pixels.wakeup()
        # print("Wake word detected")
    
    elif msg.topic == _SUB_ON_LISTENING:
        pixels.think()
    
    elif msg.topic == _SUB_ON_THINK:
        pixels.think()
    
    elif msg.topic == _SUB_ON_SAY:
        pixels.speak()
    
    elif msg.topic == _SUB_ON_TTS_FINISHED:
        pixels.off()
    
    elif msg.topic == _SUB_INTENT_ON_SUCCESS:
        pass
        # print("Got intent:", nlu_payload["intent"]["intentName"])

        # # Speak the text from the intent
        # sentence = nlu_payload["input"]   
        # publish text to speaker
        # client.publish("hermes/tts/say", json.dumps({"text": sentence, "siteId": site_id}))
    else:
        pixels.off()

    
# Create MQTT client and connect to broker
client = None

try:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect("localhost", 1883)

    while not client.is_connected():
        client.loop()
        print(client.is_connected())
except:
    print("client is not connected")

client.loop_forever()
