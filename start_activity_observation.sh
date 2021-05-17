#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
LOG_PATH="/var/tmp/sensor_logs"

mkdir -p $LOG_PATH

nohup python3 $SCRIPTPATH/autoconfigure_service.py $SCRIPTPATH/sensor_specs.json > $LOG_PATH/sensor_log_autoconfigure_service.txt &
nohup python3 $SCRIPTPATH/event_observer.py $SCRIPTPATH/sensor_specs.json "keyboard_observer" > $LOG_PATH/sensor_log_keyboard_observer.txt &
nohup python3 $SCRIPTPATH/event_observer.py $SCRIPTPATH/sensor_specs.json "mouse_observer" > $LOG_PATH/sensor_log_mouse_observer.txt &
