# Code logic for Connections.py

## Purpose of code
- To create a method of checking the connectivity of all 6 sensors, for easy to visualise, tkinter is used to create a UI, that refreshes every 500ms, and provide a real time feed back.
---

## 1. Basic Setup and Sensor Mapping

- `SENSOR_MAP`: A dictionary linking sensor numbers (1–6) to specific GPIO pins. `({1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21})`

- `SENSOR_PINS`: A list of GPIO pins used for each sensor number, extracted from `SENSOR_MAP`. `(list(SENSOR_MAP.values()))`

- GPIO is set to use **BCM (Broadcom)** pin numbering, which means to use the pins on the raspberry pi like how they were originaly designed and setup in the chip.

- Each pin in `SENSOR_PINS` is configured as:
  - An pin that takes in input
  - With a pull-up resistor enabled (`GPIO.PUD_UP`), when the sensor does not have pressure applied, its default will be in high or 1, when it has pressure applied to it, it will be low or 0.

---

## 2. Tkinter GUI Initialization

- A Tkinter `root` window is created with the title `"Sensor Connection Status"`.

- For each sensor:
  - A `Label` is created for every sensor to show its status.
  - Initial label text: `"Sensor X (Pin Y): Checking..."`.
  - Each label is added to the GUI and stored in a `labels` dictionary for easy access and updates.

---

## 3. Sensor Status Update Loop

- The `update_status()` function:
  - Reads the input from each GPIO pin.
  - If the pin reads **LOW**, the sensor is considered **Pressed**.
  - If the pin reads **HIGH**, the sensor is **Not Pressed**.
  - Updates the corresponding label text accordingly.

- The function run again in **500 milliseconds** using `root.after(500, update_status)` to keep the display live.

---

## 4. Main Loop and Cleanup

- The GUI event loop starts with `root.mainloop()`, keeping the window active.

- When the GUI is closed, the `finally` stops `root.mainloop()`and ensures that all GPIO pins are reseted properly with `GPIO.cleanup()`, preventing possible conflicts when rerunning the code

---


