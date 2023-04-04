## Home Assistant Addon: Modbus MQTT Bridge

This Home Assistant addon creates a bridge between a Modbus device and an MQTT broker. It reads data from a Modbus device and publishes it to MQTT topics at a defined interval. Entities will get automatically created. It should be able to interface with modbus devices using a cheap 2$ usb-rs485 adapter.

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

- `publish_rate`: The interval (in seconds) at which the add-on publishes data to MQTT
- `serial_port`: The path to the USB port where the Modbus device is connected
- `serial_baudrate`: The baud rate to use for serial communication with the Modbus device
- `serial_bytesize`: The number of data bits to use for serial communication with the Modbus device
- `serial_parity`: The parity scheme to use for serial communication with the Modbus device
- `serial_stopbits`: The number of stop bits to use for serial communication with the Modbus device
- `serial_timeout`: The timeout (in seconds) for serial communication with the Modbus device
- `serial_mode`: The mode (`rtu` for RTU mode, `ascii` for ASCII mode) to use for serial communication with the Modbus device
- `serial_clear_buffers_before_each_transaction`: Whether to clear the serial buffers before each Modbus transaction
- `serial_debug`: Whether to enable debug logging for serial communication
- `alternative_topics`: (optional) A JSON-formatted string specifying alternative MQTT topics and Modbus addresses to use ([example](https://github.com/MerzSebastian/hassio-ModbusMQTTBridge#default-topics-value))

# Usage

Once the add-on is installed and configured, it will automatically create MQTT sensors based on the config data you provided.

# Default topics value

```json
[
  {
    "sensor": {
      "unique_id": "power-meter_voltage_l1",
      "name": "Power TEST meter - voltage - l1",
      "state_topic": "power-meter/voltage/l1",
      "unit_of_measurement": "V"
    },
    "address": 14
  },
  {
    "sensor": {
      "unique_id": "power-meter_voltage_l2",
      "name": "Power meter - voltage - l2",
      "state_topic": "power-meter/voltage/l2",
      "unit_of_measurement": "V"
    },
    "address": 16
  },
  {
    "sensor": {
      "unique_id": "power-meter_voltage_l3",
      "name": "Power meter - voltage - l3",
      "state_topic": "power-meter/voltage/l3",
      "unit_of_measurement": "V"
    },
    "address": 18
  },
  {
    "sensor": {
      "unique_id": "power-meter_frequency",
      "name": "Power meter - frequency",
      "state_topic": "power-meter/frequency",
      "unit_of_measurement": "Hz"
    },
    "address": 20
  },
  {
    "sensor": {
      "unique_id": "power-meter_current_l1",
      "name": "Power meter - current - l1",
      "state_topic": "power-meter/current/l1",
      "unit_of_measurement": "A"
    },
    "address": 22
  },
  {
    "sensor": {
      "unique_id": "power-meter_current_l2",
      "name": "Power meter - current - l2",
      "state_topic": "power-meter/current/l2",
      "unit_of_measurement": "A"
    },
    "address": 24
  },
  {
    "sensor": {
      "unique_id": "power-meter_current_l3",
      "name": "Power meter - current - l3",
      "state_topic": "power-meter/current/l3",
      "unit_of_measurement": "A"
    },
    "address": 26
  },
  {
    "sensor": {
      "unique_id": "power-meter_wattage",
      "name": "Power meter - wattage",
      "state_topic": "power-meter/wattage",
      "unit_of_measurement": "W"
    },
    "address": 28,
    "scale": 1000
  },
  {
    "sensor": {
      "unique_id": "power-meter_wattage_l1",
      "name": "Power meter - wattage - l1",
      "state_topic": "power-meter/wattage/l1",
      "unit_of_measurement": "W"
    },
    "address": 30,
    "scale": 1000
  },
  {
    "sensor": {
      "unique_id": "power-meter_wattage_l2",
      "name": "Power meter - wattage - l2",
      "state_topic": "power-meter/wattage/l2",
      "unit_of_measurement": "W"
    },
    "address": 32,
    "scale": 1000
  },
  {
    "sensor": {
      "unique_id": "power-meter_wattage_l3",
      "name": "Power meter - wattage - l3",
      "state_topic": "power-meter/wattage/l3",
      "unit_of_measurement": "W"
    },
    "address": 34,
    "scale": 1000
  },
  {
    "sensor": {
      "unique_id": "power-meter_power-factor_l1",
      "name": "Power meter - power factor - l1",
      "state_topic": "power-meter/power-factor/l1"
    },
    "address": 54
  },
  {
    "sensor": {
      "unique_id": "power-meter_power-factor_l2",
      "name": "Power meter - power factor - l2",
      "state_topic": "power-meter/power-factor/l2"
    },
    "address": 56
  },
  {
    "sensor": {
      "unique_id": "power-meter_power-factor_l3",
      "name": "Power meter - power factor - l3",
      "state_topic": "power-meter/power-factor/l3"
    },
    "address": 58
  },
  {
    "sensor": {
      "unique_id": "power-meter_consumption",
      "name": "Power meter - consumption",
      "state_topic": "power-meter/consumption",
      "unit_of_measurement": "kWh"
    },
    "address": 256
  }
]
```

# Credits

This add-on was created by Sebastian Merz. It uses the following libraries:
minimalmodbus
paho-mqtt

# Support

If you have any issues or feature requests, please open an issue on the GitHub repository.
