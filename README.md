## Home Assistant Addon: Modbus MQTT Bridge
This Home Assistant addon creates a bridge between a Modbus device and an MQTT broker. It reads data from a Modbus device and publishes it to MQTT topics at a defined interval.

# Installation
To install this add-on, follow these steps:
1. Open the Home Assistant web interface
2. Click on the Supervisor tab
3. Click on Add-on Store
4. Add the following URL to the "Repositories" field: https://github.com/MerzSebastian/hassio-ModbusMQTTBridge
5. Click on the "Add" button
6. Find the add-on you want to install and click on it
7. Click on the "Install" button

# Configuration
The add-on can be configured using the config tab. The addon is pre-configured to work with a product called "ORNO OR-WE-517". This can be overwritten by filling the "alternative_topics" option.
Here's an overview of the available options:
* ```publish_rate```: The interval (in seconds) at which the add-on publishes data to MQTT
* ```serial_port```: The path to the USB port where the Modbus device is connected
* ```serial_baudrate```: The baud rate to use for serial communication with the Modbus device
* ```serial_bytesize```: The number of data bits to use for serial communication with the Modbus device
* ```serial_parity```: The parity scheme to use for serial communication with the Modbus device
* ```serial_stopbits```: The number of stop bits to use for serial communication with the Modbus device
* ```serial_timeout```: The timeout (in seconds) for serial communication with the Modbus device
* ```serial_mode```: The mode (```rtu``` for RTU mode, ```ascii``` for ASCII mode) to use for serial communication with the Modbus device
* ```serial_clear_buffers_before_each_transaction```: Whether to clear the serial buffers before each Modbus transaction
* ```serial_debug```: Whether to enable debug logging for serial communication
* ```alternative_topics```: (optional) A JSON-formatted string specifying alternative MQTT topics and Modbus addresses to use (example: ```[{ "topic": "test1", "address": 14 }, { "topic": "test2", "address": 16, "scale": 10 }]```)

# Usage
Once the add-on is installed and configured, it will automatically start publishing data to the specified MQTT topics at the configured interval. You can use the published data to create sensors and automations in Home Assistant.

# Default topics value
```json
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
```

# Credits
This add-on was created by Sebastian Merz. It uses the following libraries:
minimalmodbus
paho-mqtt

# Support
If you have any issues or feature requests, please open an issue on the GitHub repository.


