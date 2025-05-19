import random

def rng_app(min_value=1, max_value=100):
    print(f"Generating a random number between {min_value} and {max_value}...")
    random_number = random.randint(min_value, max_value)
    print(f"Generated Number: {random_number}")

if __name__ == '__main__':
    try:
        min_val = int(input("Enter the minimum value: "))
        max_val = int(input("Enter the maximum value: "))
        if min_val < max_val:
            rng_app(min_val, max_val)
        else:
            print("Minimum value must be less than maximum value.")
    except ValueError:
        print("Please enter valid integers.")
