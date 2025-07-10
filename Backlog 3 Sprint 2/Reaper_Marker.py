from pythonosc import udp_client
import time

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
PI_A_ADDR = "192.168.254.12"	# wlan ip
PORT = 8000

addr= "/action/41261" 	# Jump to Marker 21
addr1 = "/action/1007"  # Play
addr2 = "/action/1016"  # Stop
msg = float(1) 			# Trigger TRUE Value

send_message(PI_A_ADDR, PORT, addr, msg)  	# Jump to marker
send_message(PI_A_ADDR, PORT, addr1, msg)  	# Play
time.sleep(5)  								# Wait for 5 second to allow the play action to take effect
send_message(PI_A_ADDR, PORT, addr2, msg)  	# Stop


