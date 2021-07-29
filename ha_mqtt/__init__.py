import json
import paho.mqtt.client as mqtt
import logging


def _create_device_homeassistant_path(config_data, device_config):
    return config_data["hs_autoconfigure_prefix"] + "/" + device_config["device_type"] + "/" + device_config["name"]


def create_attributes_topic(config_data, device_data):
    return _create_device_homeassistant_path(config_data, device_data) + "/attributes"

def create_availability_topic(config_data, device_data):
    return _create_device_homeassistant_path(config_data, device_data) + "/availability"


def create_state_topic(config_data, device_data):
    return _create_device_homeassistant_path(config_data, device_data) + "/state"


def _create_command_topic(config_data, device_data):
    return _create_device_homeassistant_path(config_data, device_data) + "/set"


def _configure_device(client, auto_configure_topic, auto_config_data):
    auto_configure_json_data = json.dumps(auto_config_data)
    logging.info("Publishing auto configure data to: " + auto_configure_topic)
    logging.debug("Data: " + json.dumps(auto_configure_json_data))
    client.publish(auto_configure_topic, auto_configure_json_data)


def auto_configure_switch(client, config_data, switch_data):
    auto_config_data = {"unique_id": switch_data["id"],
                        "name": switch_data["name"],
                        "state_topic": create_state_topic(config_data, switch_data),
                        "command_topic": _create_command_topic(config_data, switch_data),
                        "device_class": switch_data["device_class"],
                        "device": {
        "ids": [config_data["device_info"]["id"]],
        "model": config_data["device_info"]["type"],
        "name": config_data["device_info"]["name"],
        "sw_version": config_data["device_info"]["firmware_version"]
    }}
    auto_configure_topic = _create_device_homeassistant_path(
        config_data, switch_data) + "/config"
    _configure_device(client, auto_configure_topic, auto_config_data)


def auto_configure_docker_update_sensor(client, config_data, sensor_data, expire_after=7200):
    sensor_data["device_type"] = "binary_sensor"
    auto_config_data = {"unique_id": sensor_data["id"],
                        "name": sensor_data["name"],
                        "value_template": "{{ value_json.update_available }}",
                        "expire_after": expire_after,
                        "payload_off": "False",
                        "payload_on": "True",
                        "state_topic": create_state_topic(config_data, sensor_data),
                        "json_attributes_topic": create_attributes_topic(config_data, sensor_data),
                        "availability" : [
                            { "topic" : create_availability_topic(config_data, sensor_data),
                               "payload_available" : "available",
                               "payload_not_available" : "unavailable"}
                        ],
                        "device": {
        "ids": [config_data["device_info"]["id"]],
        "model": config_data["device_info"]["type"],
        "name": config_data["device_info"]["name"],
        "sw_version": config_data["device_info"]["firmware_version"],
    }}
    auto_configure_topic = _create_device_homeassistant_path(
        config_data, sensor_data) + "/config"
    _configure_device(client, auto_configure_topic, auto_config_data)


def auto_configure_sensor(client, config_data, sensor_data):
    auto_config_data = {"unique_id": sensor_data["id"],
                        "name": sensor_data["name"],
                        "value_template": sensor_data["value_template"],
                        "off_delay": sensor_data["off_delay"],
                        "state_topic": create_state_topic(config_data, sensor_data),
                        "json_attributes_topic": create_attributes_topic(config_data, sensor_data),
                        "device": {
        "ids": [config_data["device_info"]["id"]],
        "model": config_data["device_info"]["type"],
        "name": config_data["device_info"]["name"],
        "sw_version": config_data["device_info"]["firmware_version"],
    }}
    auto_configure_topic = _create_device_homeassistant_path(
        config_data, sensor_data) + "/config"
    _configure_device(client, auto_configure_topic, auto_config_data)


def auto_configure_motion_sensor(client, config_data, sensor_data):
    auto_config_data = {"unique_id": sensor_data["id"],
                        "name": sensor_data["name"],
                        "state_topic": create_state_topic(config_data, sensor_data),
                        "off_delay": sensor_data["off_delay"],
                        "device_class": sensor_data["device_class"],
                        "device": {
        "ids": [config_data["device_info"]["id"]],
        "model": config_data["device_info"]["type"],
        "name": config_data["device_info"]["name"],
        "sw_version": config_data["device_info"]["firmware_version"]
    }}
    auto_configure_topic = _create_device_homeassistant_path(
        config_data, sensor_data) + "/config"
    _configure_device(client, auto_configure_topic, auto_config_data)


def connect_mqtt_client(connection_data, auth_data=None):
    client = mqtt.Client()
    if auth_data:
        client.username_pw_set(
            auth_data["user"], password=auth_data["password"])
    if connection_data["port"]:
        client.connect(connection_data["broker"], port=connection_data["port"])
    else:
        client.connect(connection_data["broker"])
    return client
