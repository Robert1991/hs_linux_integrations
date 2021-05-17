# Homeassistant Activity Sensor for Linux Computers

This repository provides activity sensors for homeassistant which can be run within linux. The provided script can be used to observe activity on the keyboard or the mouse, in order to tell homeassistant via mqtt, that there's somebody using the computer.

In order to use it, you'll need to configure the sensor_specs.json file, like in the shown example and you'll be able to run the sensors in the background. Determin which event needs to be observered, by testing the different files, which can be found in `/dev/input/` or `/proc/bus/input/devices`.

