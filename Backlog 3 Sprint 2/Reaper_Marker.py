from pythonosc import udp_client

def send_message(receiver_ip, receiver_port, address, message):
	try:
		# Create an OSC client to send messages
		client = udp_client.SimpleUDPClient(receiver_ip, receiver_port)

		# Send an OSC message to the receiver
		client.send_message(address, message)

		print("Message sent successfully.")
	except:
		print("Message not sent")

# FOR INFO: IP address and port of the receiving Raspberry Pi
PI_A_ADDR = "192.168.254.60"	# wlan ip
PORT = 6800

addr = "/action/40161" # Jump to Marker One
msg = float(1) # Trigger TRUE Value

send_message(PI_A_ADDR, PORT, addr, msg)