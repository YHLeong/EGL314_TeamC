from pythonosc import udp_client
import time
import keyboard  # Requires: pip install keyboard

def send_message(receiver_ip, receiver_port, address, message):
    try:
        client = udp_client.SimpleUDPClient(receiver_ip, receiver_port)
        client.send_message(address, message)
        print(f"Sent: {address}")
    except Exception as e:
        print(f"Failed to send {address}: {e}")

# Setup
PI_A_ADDR = "192.168.254.12"
PORT = 8000
msg = float(1)

# OSC Addresses
addr = "/action/41261"   # Marker 21
addr1 = "/action/1007"   # Play
addr2 = "/action/1016"   # Stop
addr3 = "/marker/21"     # Marker 34
addr4 = "/action/41267"  # Marker 27

# Step 1: Trigger addr4
send_message(PI_A_ADDR, PORT, addr4, msg)

# Step 2: Trigger addr3 and Play
send_message(PI_A_ADDR, PORT, addr3, msg)
send_message(PI_A_ADDR, PORT, addr1, msg)

# Step 3: Wait for 10 spacebar presses
print("Spacebar counter active. Press 10 times to continue...")
space_count = 0

while True:
    if keyboard.is_pressed("space"):
        space_count += 1
        print(f"Spacebar pressed {space_count} time(s)")
        while keyboard.is_pressed("space"):
            time.sleep(0.1)  # Debounce
    if space_count >= 10:
        break

# Step 4: Trigger addr and Play again
print("Triggering addr (Marker 21)...")
send_message(PI_A_ADDR, PORT, addr, msg)
send_message(PI_A_ADDR, PORT, addr1, msg)

# Step 5: Wait and Stop
time.sleep(5)
send_message(PI_A_ADDR, PORT, addr2, msg)          
          



