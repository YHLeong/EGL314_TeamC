import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import time              # Import time module for delays

# Use BCM numbering (GPIO numbers, not physical pin numbers)
GPIO.setmode(GPIO.BCM)

# Sensor GPIO pin mapping (sensor number to GPIO pin)
sensor_pins = {
    1: 5,
    2: 6,
    3: 19,
    4: 16,
    5: 20,
    6: 21
}

# Force threshold in seconds (adjust this to your liking)
FORCE_THRESHOLD = 0.3

# Set up each sensor pin as input with a pull-down resistor
for pin in sensor_pins.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Sensor test started. Press a sensor...")

try:
    # Main loop to continuously check sensor states
    while True:
        for sensor_id, pin in sensor_pins.items():
            # Check if the current sensor is pressed (reads HIGH)
            if GPIO.input(pin) == GPIO.HIGH:
                # Record the time when the press started
                press_start = time.time()
                
                # Wait for the sensor to be released
                while GPIO.input(pin) == GPIO.HIGH:
                    time.sleep(0.01)  # Short delay to avoid rapid re-triggering
                
                # Calculate how long the sensor was pressed
                press_duration = time.time() - press_start
                
                # Check if the press duration exceeded the force threshold
                if press_duration >= FORCE_THRESHOLD:
                    print(f"Sensor {sensor_id} was pressed with enough force ({press_duration:.2f} seconds)")

        # Small delay to reduce CPU usage
        time.sleep(0.05)

except KeyboardInterrupt:
    # Gracefully handle script exit on Ctrl+C
    print("\nExiting gracefully...")
finally:
    # Clean up GPIO settings to avoid warnings on next run
    GPIO.cleanup()