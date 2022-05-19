#!/bin/python3

import json
import sys
import logging
from ha_mqtt import connect_mqtt_client
from ha_mqtt import auto_configure_motion_sensor
from ha_mqtt import auto_configure_sensor
from ha_mqtt import auto_configure_docker_update_sensor

logging.basicConfig(filename='/var/log/autoconfigure_service.log',
                    format='%(asctime)s %(message)s', level=logging.INFO)


if len(sys.argv) != 2:
    print("Missing config file at arg 1")
    exit(1)


def autoconfigure_sensors(client, config_data):
    for sensor in config_data["sensors"]:
        logging.info("Autoconfiguring: " + sensor["name"])
        if hasattr(sensor, "device_class"):
            if sensor["device_class"] == "motion":
                auto_configure_motion_sensor(client, config_data, sensor)
        if sensor["type"] == "docker_update_sensor":
            auto_configure_docker_update_sensor(client, config_data, sensor)
        else:
            auto_configure_sensor(client, config_data, sensor)


with open(sys.argv[1]) as configuration_file:
    config_data = json.load(configuration_file)
    client = connect_mqtt_client(
        config_data["connection_data"], config_data["login"])
    autoconfigure_sensors(client, config_data)

    def on_connect(client, userdata, flags, rc):
        logging.info("Connected with result code "+str(rc))
        client.subscribe("homeassistant/status")

    def on_message(client, userdata, msg):
        logging.info(msg.topic+" "+str(msg.payload))
        if str(msg.payload) == "b'online'":
            logging.info(
                "HASS Birth message received. Autoconfiguring defined sensors...")
            autoconfigure_sensors(client, config_data)

    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
