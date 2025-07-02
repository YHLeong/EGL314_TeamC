from pythonosc import udp_client
import time

def send_message(receiver_ip, receiver_port, address, message):
	try:
		client = udp_client.SimpleUDPClient(receiver_ip, receiver_port)
		client.send_message(address, message)
		print(f"Sent to {address} with msg {message}")
	except Exception as e:
		print(f"Message not sent: {e}")

# REAPER OSC setup
REAPER_IP = "192.168.254.60"  # IP of the machine running REAPER
PORT = 6800


# PLAY
send_message(REAPER_IP, PORT, "/action/40073", 1.0)  # Play
time.sleep(3)

# STOP
send_message(REAPER_IP, PORT, "/action/1007", 1.0)   # Stop
time.sleep(3)

# TOGGLE (Play/Stop Toggle)
send_message(REAPER_IP, PORT, "/action/40044", 1.0)  # Play/Stop Toggle