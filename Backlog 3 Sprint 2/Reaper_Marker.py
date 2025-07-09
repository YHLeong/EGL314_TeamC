from pythonosc import udp_client
import keyboard  # Requires 'keyboard' package

def send_message(receiver_ip, receiver_port, address, message):
    try:
        # Create an OSC client to send messages
        client = udp_client.SimpleUDPClient(receiver_ip, receiver_port)

        # Send an OSC message to the receiver
        client.send_message(address, message)

        print(f"Message sent to {address} successfully.")
    except:
        print("Message not sent")

# FOR INFO: IP address and port of the receiving Raspberry Pi
PI_A_ADDR = "192.168.254.12"  # wlan ip
PORT = 8000

# Marker action addresses for markers 21 to 33
marker_addrs = [
    "/action/40181", # Marker 21
    "/action/40182", # Marker 22
    "/action/40183", # Marker 23
    "/action/40184", # Marker 24
    "/action/40185", # Marker 25
    "/action/40186", # Marker 26
    "/action/40187", # Marker 27
    "/action/40188", # Marker 28
    "/action/40189", # Marker 29
    "/action/40190", # Marker 30
    "/action/40191", # Marker 31
    "/action/40192", # Marker 32
    "/action/40193", # Marker 33
]

addr1 = "/action/40044" # Play/Stop toggle
msg = float(1) # Trigger TRUE Value

print("Press 1-9, 0, q, w, e to trigger markers 21-33. Press ESC to exit.")
key_map = ['1','2','3','4','5','6','7','8','9','0','q','w','e']

while True:
    event = keyboard.read_event()
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'esc':
            print("Exiting...")
            break
        if event.name in key_map:
            idx = key_map.index(event.name)
            addr = marker_addrs[idx]
            send_message(PI_A_ADDR, PORT, addr, msg)  # Jump to marker
            send_message(PI_A_ADDR, PORT, addr1, msg)  # Play
            send_message(PI_A_ADDR, PORT, addr1, msg)  # Stop