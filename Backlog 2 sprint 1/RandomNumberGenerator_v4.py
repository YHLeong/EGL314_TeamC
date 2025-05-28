import random
import time

# Predefined sequence lengths to cycle through
sequence_lengths = [4, 8, 12]
current_index = 0  # Start at 4

print("Generating sequences every 1 second. Press Ctrl+C to stop.")

try:
    while True:
        # Get current sequence length
        seq_length = sequence_lengths[current_index]

        # Generate random sequence
        sequence = [random.randint(1, 6) for _ in range(seq_length)]
        print(f"Generated sequence ({seq_length} numbers): {sequence}")

        # Move to next index, loop back if needed
        current_index = (current_index + 1) % len(sequence_lengths)

        # Wait 1 second before generating the next sequence
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting... Program stopped by user.")
