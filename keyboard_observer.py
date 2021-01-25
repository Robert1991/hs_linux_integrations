#!/usr/bin/python

import json
import sys
from ha_mqtt import create_state_topic
from ha_mqtt import auto_configure_motion_sensor
from ha_mqtt import connect_mqtt_client

from activity_observation import find_event_file
from activity_observation import observe

def publish_state_observed():
    if not client.is_connected():
        client.reconnect()
    client.publish(state_topic, "ON")

if len(sys.argv) != 3:
  print("Missing config file at arg 1 or sensor key at arg 2")
  exit(1)

with open(sys.argv[1]) as configuration_file:
  config_data = json.load(configuration_file)
  observer_config = [sensor for sensor in config_data["sensors"] if sensor["type"] == sys.argv[2]][0]

  state_topic = create_state_topic(config_data, observer_config)
  
  client = connect_mqtt_client(config_data["connection_data"], config_data["login"]) 
  auto_configure_motion_sensor(client, config_data, observer_config)

  keyboard_event_file = find_event_file(observer_config["observed_dev_event_id"])
  keyboard_event_type = observer_config["observed_dev_event_type"]

  observe(keyboard_event_file, keyboard_event_type, publish_state_observed)
  