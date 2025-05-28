import random
import keyboard  
import time

seq_length = 4
direction = 1 

print("Press 'a' to generate a random sequence. Press 'q' to quit.")

while True:
    if keyboard.is_pressed("q"):
        print("Exiting...")
        break

    if keyboard.is_pressed("a"):
        sequence = [random.randint(1, 6) for _ in range(seq_length)]
        print(f"Generated sequence ({seq_length} numbers): {sequence}")

        if direction == 1:
            if seq_length < 6:
                seq_length += 1
            else:
                direction = -1
                seq_length -= 1
        else:
            if seq_length > 4:
                seq_length -= 1
            else:
                direction = 1
                seq_length += 1

        time.sleep(0.3)  
