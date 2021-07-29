#!/bin/python3

import subprocess
import requests
import sys
from ha_mqtt import connect_mqtt_client
from ha_mqtt import auto_configure_docker_update_sensor
from ha_mqtt import create_state_topic
from ha_mqtt import create_attributes_topic
import time
import json
import logging

logging.basicConfig(filename='/var/log/private/docker_update_sensor.log',
                    format='%(asctime)s %(message)s', level=logging.INFO)


def _fetch_api_token(image_name):
    request_url = "https://auth.docker.io/token?scope=repository:" + \
        image_name + ":pull&service=registry.docker.io"

    token_response = requests.get(request_url)
    if token_response.status_code == 200:
        response_object = token_response.json()
        return response_object["token"]
    logging.debug("api token request " + request_url +
                  " failed with: \n" + str(token_response.text))
    return None


def _fetch_digest_from_docker_hub(image_name):
    query_image_name = image_name
    if len(image_name.split("/")) == 1:
        query_image_name = "library/" + image_name

    response_token = _fetch_api_token(query_image_name)
    if response_token:
        digest_request = "https://registry.hub.docker.com/v2/" + \
            query_image_name + "/manifests/latest"
        request_parameters = {
            "Accept": "application/vnd.docker.distribution.manifest.v2+json", "Authorization": ""}
        request_parameters["Authorization"] = "Bearer " + response_token
        digest_response = requests.get(
            digest_request, headers=request_parameters)
        if digest_response.status_code == 200:
            digest_response_content = digest_response.json()
            return digest_response_content["config"]["digest"]
        logging.error("digest request " + digest_request +
                      " failed with: \n" + str(digest_response.text))
    return None


def _fetch_local_digest(image_name):
    process = subprocess.Popen(["docker", "images", "-q", "--no-trunc", image_name + ":latest"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if not stderr:
        return stdout.decode("utf-8").strip("\n")
    logging.error("Getting local digest for " +
                  image_name + " failed: " + stderr)


def _new_image_available(image_name):
    digest_in_docker_hub = _fetch_digest_from_docker_hub(image_name)
    local_container_digest = _fetch_local_digest(image_name)
    if digest_in_docker_hub != local_container_digest:
        logging.info("New container digest found for: " + image_name)
        return True, digest_in_docker_hub
    logging.info("No updates found for: " + image_name)
    return False, local_container_digest


def get_sensors(config_data):
    return [sensor for sensor in config_data["sensors"] if sensor["type"] == "docker_update_sensor"]


def wait_for_sensor_autoconfigure(config_data, failover_timeout=5):
    while True:
        try:
            client = connect_mqtt_client(
                config_data["connection_data"], config_data["login"])
            for update_sensor in get_sensors(config_data):
                auto_configure_docker_update_sensor(
                    client, config_data, update_sensor)
            return client
        except:
            logging.error(
                "Unexpected error while auto configuring:", sys.exc_info())
            time.sleep(failover_timeout)


def observe_container_versions(config_data, time_out=1900, in_between_request_timeout=5):
    while True:
        for sensor in get_sensors(config_data):
            sensor_state_topic = create_state_topic(config_data, sensor)
            sensor_attributes_topic = create_attributes_topic(
                config_data, sensor)

            logging.info("Checking for updates for: " + sensor["name"])
            image_available, image_digest = _new_image_available(
                sensor["image_name"])
            mqtt_data = {"update_available": image_available,
                         "image": sensor["image_name"],
                         "digest": image_digest}
            try:
                if not client.is_connected():
                    client.reconnect()
                client.publish(sensor_state_topic, json.dumps(mqtt_data))
                client.publish(sensor_attributes_topic, json.dumps(mqtt_data))
            except:
                logging.error("Unexpected error:", sys.exc_info()[0])
            time.sleep(in_between_request_timeout)
        logging.info("Sleeping for " + str(time_out) +
                     " seconds before checking again...")
        time.sleep(time_out)


if len(sys.argv) != 2:
    print("Missing config file at arg 1 or sensor key at arg 2")
    exit(1)

with open(sys.argv[1]) as configuration_file:
    config_data = json.load(configuration_file)
    client = wait_for_sensor_autoconfigure(config_data)
    observe_container_versions(config_data)
