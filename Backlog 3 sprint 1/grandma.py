from pythonosc import udp_client, osc_message_builder
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

if __name__ == "__main__":
    LAPTOP_IP = "192.168.8.132"		
    PORT = 8000                  
    addr = "/gma3/cmd"

client = udp_client.SimpleUDPClient(LAPTOP_IP, PORT)

send_message(LAPTOP_IP, PORT, addr, "On Sequence 2")
print("Sequence 2 on")
time.sleep(2)
send_message(LAPTOP_IP, PORT, addr, "Goto Sequence 2 Cue 2")
print("Go Sequence 2 cue 2")
time.sleep(2)
send_message(LAPTOP_IP, PORT, addr, "Go+ Sequence 2")
print("Go Sequence 2 Next cue")
time.sleep(2)
send_message(LAPTOP_IP, PORT, addr, "Go Sequence 2 cue 1")
print("Go Sequence 2 cue 1")
time.sleep(2)

