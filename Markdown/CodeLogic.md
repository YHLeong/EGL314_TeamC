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
  - With a pull-up resistor enabled (`GPIO.PUD_UP`), when the sensor does not have pressure applied, its default will be in high(1), when it has pressure applied to it, it will be low(0).

---

## 2. Tkinter GUI Setup

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

# Code logic for randomiser.py

## Purpose

To show that a functioning randomiser has been incorporated, and basic game logic has been establised. 

---

## 1. Basic Setup and Sensor Mapping

- Necessary libraries has been imported, `RPi.GPIO`, `tkinter` and `Random`.
  - `RPi.GPIO` to interact with the GPIO pins
  - `tkinter` for the GUI
  - `random` for the picking of a random sensor.

- It then creates a dictionary that maps sensor numbers (1 to 6) to GPIO pins:
  - `SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}`

- This there for gives each sensor a corresponding GPIO pin

---

## 2. Tkinter GUI Setup

- Using tkinter, a simple window with a title of `Sensor Randomiser`is created.
  - `root = tk.Tk()`, `root.title("Sensor Randomizer")`
- It has a title and two labels: 
  - one for instructions and 
  - one that updates to show which sensor the user should press. 

- The initial text is set to "Waiting..." until the first sensor is chosen.
---

## 3. Randomiser
- The program uses a function called `randomize_sensor()` to pick a random sensor numbers. 

- It then updates the label to show which sensor to press:
  - `sensor_label.config(text=f"Press sensor {current_sensor}")`
---

## 4. Sensor Checking

- A function called `check_sensor()` is used to continuously check if the correct sensor has been pressed.
- This function runs every 100 milliseconds using `root.after(100, check_sensor)`.

- It compares the GPIO input of the selected sensor:
  - If the input is `LOW`, this means the sensor is pressed.

- When the correct sensor is pressed:
  - A message is printed: `Sensor X pressed!`
  - The program waits 2 seconds using `root.after(2000, randomize_sensor)` before choosing a new random sensor.
  - This delay avoids instantly triggering the next round and messing up the game.
  - A `waiting` flag is used to ensure the sensor press is only handled once per round.

---

## 5. Game Start Logic

- Before starting the GUI, the following two functions are called:
  - `randomize_sensor()` picks and displays the first sensor
  - `check_sensor()` starts the loop to monitor input

- These two lines start the game:
  - `randomize_sensor()`
  - `check_sensor()`

---

## 6. Main Loop and Cleanup

- The GUI event loop starts with `root.mainloop()`, keeping the window active.

- When the GUI is closed, the `finally` stops `root.mainloop()`and ensures that all GPIO pins are reseted properly with `GPIO.cleanup()`, preventing possible conflicts when rerunning the code

