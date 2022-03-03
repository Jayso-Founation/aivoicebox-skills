import time
import paho.mqtt.client as mqtt
import board
import busio

import adafruit_vl53l0x

# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

vl53.measurement_timing_budget = 200000

def on_disconnect(client, userdata, flags, rc):
    """Called when disconnected from MQTT broker."""
    client.reconnect()

# Create MQTT client and connect to broker
client = None

try:
    client = mqtt.Client()
    client.on_disconnect = on_disconnect
    client.connect("localhost", 1883)
    while not client.is_connected():
        client.loop()
        print(client.is_connected())
except:
    print("client is not connected")

with vl53.continuous_mode():
    count = 0
    while True:
        time.sleep(0.1)
        client.loop()
        curTime = time.time()

        if vl53.range < 100:
            count = count + 1
        
        if count > 2:
            # print("HotWordDetected")
            client.publish("hermes/hotword/default/detected",b'{"modelId": "default", "modelVersion": "", "modelType": "personal", "currentSensitivity": 1.0, "siteId": "aivoicebox", "sessionId": null, "sendAudioCaptured": null, "lang": null, "customEntities": null}')
            count = 0
        