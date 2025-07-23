import time
import RPi.GPIO as GPIO
from pythonosc import udp_client

SENSOR_MAP = {
    1: 22,
    2: 6,
    3: 19,
    4: 16,
    5: 20,
    6: 21
}

SERVER_IP   = "192.168.254.108"
SERVER_PORT = 8001

osc_client = udp_client.SimpleUDPClient(SERVER_IP, SERVER_PORT)

GPIO.setmode(GPIO.BCM)
for pin in SENSOR_MAP.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

sensor_states = {s: False for s in SENSOR_MAP}

try:
    while True:
        for sensor_num, pin in SENSOR_MAP.items():
            pressed = GPIO.input(pin) == GPIO.LOW
            if pressed != sensor_states[sensor_num]:
                sensor_states[sensor_num] = pressed
                if pressed:
                    print(f"Sensor {sensor_num} Pressed")
                    osc_client.send_message("/print", [f"Sensor {sensor_num} Pressed"])
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Terminated by user.")