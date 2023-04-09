import json
from flask import Flask, send_from_directory, request
import os, sys
import yaml
import glob
import paho.mqtt.client as mqtt
import requests
import threading
import minimalmodbus
import time
import struct
import binascii
import uuid

# MQTT Setup
mqtt_response = requests.get("http://supervisor/services/mqtt", headers={ "Authorization": "Bearer " + os.environ.get('SUPERVISOR_TOKEN') }).json()
if "data" not in mqtt_response.keys():
    sys.exit('FATAL ERROR | Seems like no mqtt service could be found. Are you sure you installed Mosquitto?')
else:
    mqtt_response = mqtt_response["data"]
client = mqtt.Client()
client.username_pw_set(username=mqtt_response["username"],password=mqtt_response["password"])
client.connect(mqtt_response["host"], mqtt_response["port"], 60)


def getDevicesFromFolder():
    folder_path = "devices"
    objects = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml"):
            with open(os.path.join(folder_path, filename), "r") as file:
                data = yaml.safe_load(file)
            objects.append(data)
    return objects

devices_from_folder = getDevicesFromFolder()
def get_device_by_device_id(device_id):
    return [x for x in devices_from_folder if x["unique_id"] == device_id][0]

class ModbusTask:
    def __init__(self):
        self._running = True
    def terminate(self):
        self._running = False
    def run(self, mqtt_client, device_info, registered_device):
        modbus = minimalmodbus.Instrument(registered_device["serial_port"], registered_device["slave_address"])
        modbus.serial.baudrate = device_info["serial"]["baudrate"]
        modbus.serial.bytesize = device_info["serial"]["bytesize"]
        modbus.serial.parity = device_info["serial"]["parity"]
        modbus.serial.stopbits = device_info["serial"]["stopbits"]
        modbus.serial.timeout = device_info["serial"]["timeout"]
        modbus.mode = device_info["serial"]["mode"]
        modbus.clear_buffers_before_each_transaction = device_info["serial"]["clear_buffers_before_each_transaction"]
        modbus.debug = device_info["serial"]["debug"]
        to_scaled_float = lambda v,scale=1:round(struct.unpack('>f',binascii.unhexlify(('00000000' if (r:=hex(v)[2:])=='0' else r.zfill(8))))[0]*scale,2)
        # read_address = lambda address,scale=1:to_scaled_float(modbus.read_long(address), scale)
        read_address = lambda address,scale=1:round(modbus.read_float(address, functioncode=3, number_of_registers=2) * scale, 2)
        # def read_address(addr, scale):
        #     return 2 * scale
        while self._running:
            for sensor in device_info["sensors"]:
                payload = read_address(sensor["address"], sensor["scale"] if "scale" in sensor.keys() else 1)
                mqtt_client.publish(registered_device["unique_id"]+"/"+sensor["name"].replace(" ", "_"), payload)
            time.sleep(registered_device["poll_rate"])

thread_reg = []
def stop_thread_by_unique_id(unique_id):
    item = [x for x in thread_reg if x["unique_id"] == unique_id][0]
    item["terminate"]()
    thread_reg = [x for x in thread_reg if x["unique_id"] != unique_id]

# Start threads of already registered devices
if os.path.exists("/data/devices.yaml"):
    with open("/data/devices.yaml", 'r') as f:
        config = yaml.safe_load(f)
    for device in config['devices']:
        task = ModbusTask()
        t1 = threading.Thread(target=task.run, args=(client, get_device_by_device_id(device["device_id"]), device))
        t1.start()
        thread_reg.append({"unique_id": device["unique_id"], "terminate": task.terminate})


# API Setup
app = Flask(__name__)

# UI Endpoints
@app.route('/')
def index():
    return send_from_directory('ui/src', 'index.html')
@app.route('/<path:path>')
def ui(path):
    return send_from_directory('ui/src', path)

# API Endpoints
@app.route('/api/devices')
def api_devices():
    return json.dumps(devices_from_folder)

@app.route('/api/serial')
def api_get_serial_ports():
    return json.dumps(glob.glob('/dev/tty[A-Za-z]*') + glob.glob('/dev/serial/by-id/*'))

@app.route('/api/monitor/devices', methods = ['GET'])
def api_monitored_devices_get():
    if os.path.exists("/data/devices.yaml"):
        with open("/data/devices.yaml", 'r') as f:
            yaml_obj = yaml.safe_load(f)
        return json.dumps(yaml_obj["devices"])
    else:
        return json.dumps([])

@app.route('/api/monitor/devices', methods = ['POST'])
def api_monitored_devices_post():
    data = request.get_json()
    data["unique_id"] = str(uuid.uuid4())
    device_info = get_device_by_device_id(data["device_id"])
    device_data = {
        "identifiers": [data["unique_id"]],
        "name": device_info["name"],
        "model": device_info["product_name"],
        "manufacturer": device_info["company_name"]
    }
    for sensor in device_info["sensors"]:
        message = {
            "name": sensor["name"],
            "object_id": data["unique_id"] + "_" + sensor["name"].replace(" ", "_"),
            "unique_id": data["unique_id"] + "_" + sensor["name"].replace(" ", "_"),
            "state_topic": data["unique_id"] + "/" + sensor["name"].replace(" ", "_"),
            "device": device_data,
        }
        if 'icon' in sensor.keys():
            message['icon'] = sensor['icon']
        if 'unit' in sensor.keys():
            message['unit_of_measurement'] = sensor['unit']
        client.publish(f'homeassistant/sensor/{data["unique_id"] + "_" + sensor["name"].replace(" ", "_")}/config', json.dumps(message))


    task = ModbusTask()
    t1 = threading.Thread(target=task.run, args=(client, device_info, data))
    t1.start()
    thread_reg.append({"unique_id": data["unique_id"], "terminate": task.terminate})

    if not os.path.exists("/data/devices.yaml"):
        config = {'devices': [data]}
        with open("/data/devices.yaml", 'w') as f:
            yaml.dump(config, f)
    else:
        with open("/data/devices.yaml", 'r') as f:
            config = yaml.safe_load(f)
        config['devices'].append(data)
        with open("/data/devices.yaml", 'w') as f:
            yaml.dump(config, f)
    return json.dumps(data)

@app.route('/api/monitor/devices/<unique_id>', methods = ['DELETE'])
def api_monitored_devices_delete(unique_id):
    stop_thread_by_unique_id(unique_id)
    # Delete from devices.yaml
    devices_file = '/data/devices.yaml'
    with open(devices_file, 'r') as f:
        devices = yaml.load(f, Loader=yaml.FullLoader)
    new_devices = []
    for device in devices['devices']:
        if device['unique_id'] != unique_id:
            new_devices.append(device)
        else:
            device_to_delete = device
    with open(devices_file, 'w') as f:
        yaml.dump({'devices': new_devices}, f)

    # Delete the device and sensor entities
    device_info = get_device_by_device_id(device_to_delete['device_id'])
    for sensor in device_info['sensors']:
        topic = "homeassistant/sensor/{}/config".format(device_to_delete["unique_id"] + "_" + sensor["name"].replace(" ", "_"))
        client.publish(topic, payload=None, retain=True)
    return "ok"


app.run(host='0.0.0.0', port=8099)
