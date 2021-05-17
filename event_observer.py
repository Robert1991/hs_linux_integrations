#!/usr/bin/python3.8

import json
import sys
import time
from ha_mqtt import create_state_topic
from ha_mqtt import auto_configure_motion_sensor
from ha_mqtt import connect_mqtt_client

from activity_observation import find_event_file
from activity_observation import observe


def publish_state_observed():
  try:
    if not client.is_connected():
        client.reconnect()
    client.publish(state_topic, "ON")
  except:
    print("Unexpected error:", sys.exc_info()[0])

def get_observer_config(config_data):
  return [sensor for sensor in config_data["sensors"] if sensor["type"] == sys.argv[2]][0]

def wait_for_sensor_autoconfigure(config_data, failover_timeout=5):
  while True:
    try:
      client = connect_mqtt_client(
          config_data["connection_data"], config_data["login"])
      auto_configure_motion_sensor(
          client, config_data, get_observer_config(config_data))
      return client
    except:
      print("Unexpected error while auto configuring:", sys.exc_info())
      time.sleep(failover_timeout)

def observe_activity(config_data, failover_timeout=5):
    while True:
      try:
        observer_config = get_observer_config(config_data)
        event_file = find_event_file(observer_config["observed_dev_event_id"])
        if event_file:
          event_type = observer_config["observed_dev_event_type"]
          observe(event_file, event_type, publish_state_observed)
        else:
          print("requested event not found: " +
                observer_config["observed_dev_event_id"])
          time.sleep(failover_timeout)
      except:
        print("Unexpected error while observing activity:", sys.exc_info())
        time.sleep(failover_timeout)

if len(sys.argv) != 3:
  print("Missing config file at arg 1 or sensor key at arg 2")
  exit(1)

with open(sys.argv[1]) as configuration_file:
  config_data = json.load(configuration_file)
  observer_config = [sensor for sensor in config_data["sensors"]
                     if sensor["type"] == sys.argv[2]][0]

  state_topic = create_state_topic(config_data, observer_config)
  client = wait_for_sensor_autoconfigure(config_data)
  observe_activity(config_data)
