#!/bin/python3

import json
import sys
from ha_mqtt import connect_mqtt_client
from ha_mqtt import auto_configure_motion_sensor
from ha_mqtt import auto_configure_sensor

if len(sys.argv) != 2:
    print("Missing config file at arg 1")
    exit(1)

def autoconfigure_sensors(client, config_data):
    for sensor in config_data["sensors"]:
        if hasattr(sensor, "device_class"):
            if sensor["device_class"] == "motion":
                auto_configure_motion_sensor(client, config_data, sensor)
        else:
            auto_configure_sensor(client, config_data, sensor)

with open(sys.argv[1]) as configuration_file:
    config_data = json.load(configuration_file)
    client = connect_mqtt_client(config_data["connection_data"], config_data["login"]) 
    autoconfigure_sensors(client, config_data)
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("homeassistant/status")

    def on_message(client, userdata, msg):
        if str(msg.payload) == "b'online'":
            autoconfigure_sensors(client, config_data)
        print(msg.topic+" "+str(msg.payload))
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()