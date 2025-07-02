from pythonosc import udp_client

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

# Examples
send_message(REAPER_IP, PORT, "/action/40044", 1.0)  # Play/Stop
send_message(REAPER_IP, PORT, "/action/1007", 1.0)   # Stop
send_message(REAPER_IP, PORT, "/action/40073", 1.0)  # Play