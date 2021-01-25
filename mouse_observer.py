from activity_observation import find_event_file

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

if len(sys.argv) != 2:
  print("Missing config file at arg 1")
  exit(1)


with open(sys.argv[1]) as configuration_file:
  config_data = json.load(configuration_file)
  state_topic = create_state_topic(config_data, "mouse_observer")
  
  client = connect_mqtt_client(config_data["connection_data"], config_data["login"]) 
  auto_configure_motion_sensor(client, config_data, "mouse_observer")

  mouse_event_file = find_event_file(config_data["mouse_observer"]["observed_dev_event_id"])
  mouse_event_type = config_data["mouse_observer"]["observed_dev_event_type"]
  observe(mouse_event_file, mouse_event_type, publish_state_observed)
