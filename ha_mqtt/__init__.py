import json
import paho.mqtt.client as mqtt

def _create_device_homeassistant_path(config_data, device_key):
    return config_data["hs_autoconfigure_prefix"] + "/" + config_data[device_key]["device_type"] + "/" + config_data[device_key]["name"]

def create_state_topic(config_data, device_key):
    return _create_device_homeassistant_path(config_data, device_key) + "/state"    

def auto_configure_motion_sensor(client, config_data, sensor_key):
    auto_config_data = {"unique_id": config_data[sensor_key]["id"],
            "name": config_data[sensor_key]["name"],
            "state_topic": create_state_topic(config_data, sensor_key),
            "off_delay" : config_data[sensor_key]["off_delay"],
            "device_class" : config_data[sensor_key]["device_class"],
            "device": {
                "ids": [config_data["device_info"]["id"]],
                "model": config_data["device_info"]["type"],
                "name": config_data["device_info"]["name"],
                "sw_version": config_data["device_info"]["firmware_version"]
            }}
    auto_configure_topic = _create_device_homeassistant_path(config_data, sensor_key) + "/config"
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