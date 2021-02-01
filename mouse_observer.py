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
  sensor_data = next(filter(lambda x: x["type"] == "mouse_observer", config_data["sensors"]))
  state_topic = create_state_topic(config_data, sensor_data)
  
  client = connect_mqtt_client(config_data["connection_data"], config_data["login"]) 
  auto_configure_motion_sensor(client, config_data, sensor_data)

  mouse_event_file = find_event_file(sensor_data["observed_dev_event_id"])
  mouse_event_type = sensor_data["observed_dev_event_type"]
  observe(mouse_event_file, mouse_event_type, publish_state_observed)
