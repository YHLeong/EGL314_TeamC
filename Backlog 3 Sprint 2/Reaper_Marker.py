from pythonosc import udp_client
import time

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

# Step 1: Trigger addr4 (Marker 27)
print("Triggering addr4 (Marker 27)...")
send_message(PI_A_ADDR, PORT, addr4, msg)
send_message(PI_A_ADDR, PORT, addr1, msg)
time.sleep(1)  # Small delay for marker jump

# Step 2: Trigger addr3 (Marker 34) and Play
print("Triggering addr3 (Marker 34) and Play...")
send_message(PI_A_ADDR, PORT, addr3, msg)
send_message(PI_A_ADDR, PORT, addr1, msg)

# Step 3: Wait for 10 seconds then continue
print("Waiting 10 seconds...")
time.sleep(10)

# Step 4: Trigger addr (Marker 21) and Play
print("Triggering addr (Marker 21) and Play...")
send_message(PI_A_ADDR, PORT, addr, msg)
send_message(PI_A_ADDR, PORT, addr1, msg)

# Step 5: Wait 5 seconds and Stop
print("Playing for 5 seconds...")
time.sleep(5)
print("Stopping playback...")
send_message(PI_A_ADDR, PORT, addr2, msg)