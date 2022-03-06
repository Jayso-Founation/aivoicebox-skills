import time
import paho.mqtt.client as mqtt
import board
import busio
import json
import adafruit_vl53l0x

# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

vl53.measurement_timing_budget = 200000

detection = True

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

def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    client.reconnect()

def on_message(client, userdata, msg):
    """Called each time a message is received on a subscribed topic."""
    if msg.topic == _SUB_LEDS_ON_ERROR or msg.topic == _SUB_ON_TTS_FINISHED or msg.topic == _SUB_INTENT_ON_SUCCESS:
        detection = True
        
# Create MQTT client and connect to broker
client = None

try:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.loop_start()
    client.connect("localhost", 1883)
except Exception as e:
    print(e)

try:
    with vl53.continuous_mode():
        count = 0
        while True:
            time.sleep(0.1)
            curTime = time.time()
            if vl53.range < 100 and detection == True:
                count = count + 1
            if count > 2:
                print("HotWordDetected")
                client.publish("hermes/hotword/default/detected",b'{"modelId": "default", "modelVersion": "", "modelType": "personal", "currentSensitivity": 1.0, "siteId": "aivoicebox", "sessionId": null, "sendAudioCaptured": null, "lang": null, "customEntities": null}')
                count = 0
                detection = False
except Exception as e:
    print(e)
        