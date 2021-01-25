import json
import paho.mqtt.client as mqtt

def _create_device_homeassistant_path(config_data, device_config):
    return config_data["hs_autoconfigure_prefix"] + "/" + device_config["device_type"] + "/" + device_config["name"]

def create_state_topic(config_data, device_config):
    return _create_device_homeassistant_path(config_data, device_config) + "/state"    

def auto_configure_motion_sensor(client, config_data, device_config):
    auto_config_data = {"unique_id": device_config["id"],
            "name": device_config["name"],
            "state_topic": create_state_topic(config_data, device_config),
            "off_delay" : device_config["off_delay"],
            "device_class" : device_config["device_class"],
            "device": {
                "ids": [config_data["device_info"]["id"]],
                "model": config_data["device_info"]["type"],
                "name": config_data["device_info"]["name"],
                "sw_version": config_data["device_info"]["firmware_version"]
            }}
    auto_configure_topic = _create_device_homeassistant_path(config_data, device_config) + "/config"
    auto_configure_json_data = json.dumps(auto_config_data)
    print("Publishing auto configure data to: " + auto_configure_topic)
    print("Data: " + json.dumps(auto_configure_json_data))
    client.publish(auto_configure_topic, auto_configure_json_data)


def connect_mqtt_client(connection_data, auth_data=None):
  client = mqtt.Client()
  if auth_data:
    client.username_pw_set(auth_data["user"], password=auth_data["password"])
  if connection_data["port"]:
    client.connect(connection_data["broker"], port=connection_data["port"])
  else:
    client.connect(connection_data["broker"])
  return client