import json
import minimalmodbus
import struct
import binascii
import paho.mqtt.client as mqtt
import time
import requests
import os
from datetime import datetime

log = lambda value: os.system(f'echo \'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} | {str(value)}\'') if hass_options["logging"] else lambda:None 

mqtt_response = requests.get("http://supervisor/services/mqtt", headers={
    "Authorization": "Bearer " + os.environ.get('SUPERVISOR_TOKEN')
}).json()["data"]

hass_options = json.load(open('/data/options.json'))
mqtt_user = mqtt_response["username"]
mqtt_password = mqtt_response["password"]
mqtt_server_address = mqtt_response["host"]
mqtt_server_port = mqtt_response["port"]
serial_port = hass_options["serial_port"]
interval = hass_options["publish_rate"]

client = mqtt.Client()
client.username_pw_set(username=mqtt_user,password=mqtt_password)
client.connect(mqtt_server_address, mqtt_server_port, 60)

modbus = minimalmodbus.Instrument(serial_port, 1)
modbus.serial.baudrate = hass_options["serial_baudrate"]
modbus.serial.bytesize = hass_options["serial_bytesize"]
modbus.serial.parity = hass_options["serial_parity"]
modbus.serial.stopbits = hass_options["serial_stopbits"]
modbus.serial.timeout = hass_options["serial_timeout"]
modbus.mode = hass_options["serial_mode"]
modbus.clear_buffers_before_each_transaction = hass_options["serial_clear_buffers_before_each_transaction"]
modbus.debug = hass_options["serial_debug"]

to_scaled_float=lambda v,scale=1:round(struct.unpack('>f',binascii.unhexlify(('00000000' if (r:=hex(v)[2:])=='0' else r.zfill(8))))[0]*scale,2)
read_address=lambda address,scale=1:to_scaled_float(modbus.read_long(address), scale)

topic_address_map = [
    { "topic": "power-meter/voltage/l1", "address": 14 },
    { "topic": "power-meter/voltage/l2", "address": 16 },
    { "topic": "power-meter/voltage/l3", "address": 18 },
    { "topic": "power-meter/frequency", "address": 20 },
    { "topic": "power-meter/current/l1", "address": 22 },
    { "topic": "power-meter/current/l2", "address": 24 },
    { "topic": "power-meter/current/l3", "address": 26 },
    { "topic": "power-meter/wattage", "address": 28, "scale": 1000 },
    { "topic": "power-meter/wattage/l1", "address": 30, "scale": 1000 },
    { "topic": "power-meter/wattage/l2", "address": 32, "scale": 1000 },
    { "topic": "power-meter/wattage/l3", "address": 34, "scale": 1000 },
    { "topic": "power-meter/power-factor/l1", "address": 54 },
    { "topic": "power-meter/power-factor/l2", "address": 56 },
    { "topic": "power-meter/power-factor/l3", "address": 58 },
    { "topic": "power-meter/consumption", "address": 256 }
]

topic_address_map = json.loads(hass_options["alternative_topics"]) if "alternative_topics" in hass_options else topic_address_map

def publish(client, topic, payload):
    log(f'MQTT Publish => Topic: { topic }, Payload: { payload }')
    client.publish(topic, payload)

while True:
    for el in topic_address_map:
        try:
            publish(client, el["topic"], read_address(el["address"], el["scale"] if "scale" in el else 1))
        except:
            log("Seems like there went something wrong while reading from the serial adapter or publishing the data.")
    time.sleep(interval)
    