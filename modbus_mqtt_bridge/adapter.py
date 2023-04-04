import json
import minimalmodbus
import struct
import binascii
import paho.mqtt.client as mqtt
import time
import requests
import os
import subprocess
from datetime import datetime

log = lambda value: subprocess.run(f'echo "{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} | {str(value)}"', shell=True) if hass_options['logging'] else lambda: None
hass_options = json.load(open('/data/options.json'))
mqtt_response = requests.get("http://supervisor/services/mqtt", headers={ "Authorization": "Bearer " + os.environ.get('SUPERVISOR_TOKEN') }).json()["data"]

# MQTT Setup
client = mqtt.Client()
client.username_pw_set(username=mqtt_response["username"],password=mqtt_response["password"])
client.connect(mqtt_response["host"], mqtt_response["port"], 60)

# Modbus setup
modbus = minimalmodbus.Instrument(hass_options["serial_port"], 1)
modbus.serial.baudrate = hass_options["serial_baudrate"]
modbus.serial.bytesize = hass_options["serial_bytesize"]
modbus.serial.parity = hass_options["serial_parity"]
modbus.serial.stopbits = hass_options["serial_stopbits"]
modbus.serial.timeout = hass_options["serial_timeout"]
modbus.mode = hass_options["serial_mode"]
modbus.clear_buffers_before_each_transaction = hass_options["serial_clear_buffers_before_each_transaction"]
modbus.debug = hass_options["serial_debug"]

def publish(client, topic, payload):
    log(f'MQTT Publish => Topic: { topic }, Payload: { payload }')
    client.publish(topic, payload)

to_scaled_float = lambda v,scale=1:round(struct.unpack('>f',binascii.unhexlify(('00000000' if (r:=hex(v)[2:])=='0' else r.zfill(8))))[0]*scale,2)
read_address = lambda address,scale=1:to_scaled_float(modbus.read_long(address), scale)

topic_address_map = [
    { "sensor": { "unique_id": "power-meter_voltage_l1", "name": "Power meter - voltage - l1", "state_topic": "power-meter/voltage/l1", "unit_of_measurement": "V" }, "address": 14 },
    { "sensor": { "unique_id": "power-meter_voltage_l2", "name": "Power meter - voltage - l2", "state_topic": "power-meter/voltage/l2", "unit_of_measurement": "V" }, "address": 16 },
    { "sensor": { "unique_id": "power-meter_voltage_l3", "name": "Power meter - voltage - l3", "state_topic": "power-meter/voltage/l3", "unit_of_measurement": "V" }, "address": 18 },
    { "sensor": { "unique_id": "power-meter_frequency", "name": "Power meter - frequency", "state_topic": "power-meter/frequency", "unit_of_measurement": "Hz" }, "address": 20 },
    { "sensor": { "unique_id": "power-meter_current_l1", "name": "Power meter - current - l1", "state_topic": "power-meter/current/l1", "unit_of_measurement": "A" }, "address": 22 },
    { "sensor": { "unique_id": "power-meter_current_l2", "name": "Power meter - current - l2", "state_topic": "power-meter/current/l2", "unit_of_measurement": "A" }, "address": 24 },
    { "sensor": { "unique_id": "power-meter_current_l3", "name": "Power meter - current - l3", "state_topic": "power-meter/current/l3", "unit_of_measurement": "A" }, "address": 26 },
    { "sensor": { "unique_id": "power-meter_wattage", "name": "Power meter - wattage", "state_topic": "power-meter/wattage", "unit_of_measurement": "W" }, "address": 28, "scale": 1000 },
    { "sensor": { "unique_id": "power-meter_wattage_l1", "name": "Power meter - wattage - l1", "state_topic": "power-meter/wattage/l1", "unit_of_measurement": "W" }, "address": 30, "scale": 1000 },
    { "sensor": { "unique_id": "power-meter_wattage_l2", "name": "Power meter - wattage - l2", "state_topic": "power-meter/wattage/l2", "unit_of_measurement": "W" }, "address": 32, "scale": 1000 },
    { "sensor": { "unique_id": "power-meter_wattage_l3", "name": "Power meter - wattage - l3", "state_topic": "power-meter/wattage/l3", "unit_of_measurement": "W" }, "address": 34, "scale": 1000 },
    { "sensor": { "unique_id": "power-meter_power-factor_l1", "name": "Power meter - power factor - l1", "state_topic": "power-meter/power-factor/l1" }, "address": 54 },
    { "sensor": { "unique_id": "power-meter_power-factor_l2", "name": "Power meter - power factor - l2", "state_topic": "power-meter/power-factor/l2" }, "address": 56 },
    { "sensor": { "unique_id": "power-meter_power-factor_l3", "name": "Power meter - power factor - l3", "state_topic": "power-meter/power-factor/l3" }, "address": 58 },
    { "sensor": { "unique_id": "power-meter_consumption", "name": "Power meter - consumption", "state_topic": "power-meter/consumption", "unit_of_measurement": "kWh" }, "address": 256 }
]

topic_address_map = json.loads(hass_options["alternative_topics"]) if "alternative_topics" in hass_options else topic_address_map

for el in topic_address_map:
    publish(client, "homeassistant/sensor", json.dumps(el["sensor"]))
    publish(client, f'homeassistant/sensor/{el["sensor"]["unique_id"]}/config', json.dumps(el["sensor"]))

while True:
    for el in topic_address_map:
        try:
            publish(client, el["sensor"]["state_topic"], read_address(el["address"], el["scale"] if "scale" in el else 1))
        except:
            log("Seems like there went something wrong while reading from the serial adapter or publishing the data.")
    time.sleep(hass_options["publish_rate"])
