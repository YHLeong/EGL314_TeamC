import random
import keyboard  
import time

# Predefined sequence lengths to cycle through
sequence_lengths = [4, 8, 12]
current_index = 0  # Start at 4

print("Press 'a' to cycle sequence lengths (4 → 8 → 12 → 4...). Press 'q' to quit.")

while True:
    if keyboard.is_pressed("q"):
        print("Exiting...")
        break

    if keyboard.is_pressed("a"):
        # Get current sequence length
        seq_length = sequence_lengths[current_index]

        # Generate random sequence
        sequence = [random.randint(1, 6) for _ in range(seq_length)]
        print(f"Generated sequence ({seq_length} numbers): {sequence}")

        # Move to next index, loop back if needed
        current_index = (current_index + 1) % len(sequence_lengths)

        # Prevent rapid re-triggering from one key press
        while keyboard.is_pressed("a"):
            time.sleep(0.1)

 
