import re
import struct
import time

def find_event_file(event_id):
    with open("/proc/bus/input/devices") as devices:
        device_lines = devices.readlines()
        pattern = re.compile("Handlers|EV=")
        handlers = list(filter(pattern.search, device_lines))
        pattern = re.compile("EV=" + event_id)
        for idx, elt in enumerate(handlers):
            if pattern.search(elt):
                line = handlers[idx - 1]
        pattern = re.compile("event[0-9]")
        return "/dev/input/" + pattern.search(line).group(0)
    return None

def observe(event_file, event_type, methodWhenObserved, timeout_after_observe = 10):
    FORMAT = 'llHHI'
    EVENT_SIZE = struct.calcsize(FORMAT)
    in_file = open(event_file, "rb")
    event = in_file.read(EVENT_SIZE)

    while True:
        (_, _, type, code, value) = struct.unpack(FORMAT, event)
        if code != 0 and type == event_type and value == 1:
            in_file.close()
            methodWhenObserved()
            time.sleep(timeout_after_observe)
            in_file = open(event_file, "rb")
    
        event = in_file.read(EVENT_SIZE)
