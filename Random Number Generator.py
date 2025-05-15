#RNG
import random

def generate_random_sequence(length=6, min_value=1, max_value=6, unique=False):
    if unique:
        if max_value - min_value + 1 < length:
            raise ValueError("Range too small for unique numbers of this length.")
        return random.sample(range(min_value, max_value + 1), length)
    else:
        return [random.randint(min_value, max_value) for _ in range(length)]

sequence = generate_random_sequence(length=6, min_value=1, max_value=6, unique=False)
print("Generated Sequence:", sequence)


