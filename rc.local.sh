#!/bin/sh -e

sudo nohup python3 /home/robert/hs_python_linux_integrations/keyboard_observer.py /home/robert/hs_python_linux_integrations/sensor_specs.json &
sudo nohup python3 /home/robert/hs_python_linux_integrations/mouse_observer.py /home/robert/hs_python_linux_integrations/sensor_specs.json &

exit 0