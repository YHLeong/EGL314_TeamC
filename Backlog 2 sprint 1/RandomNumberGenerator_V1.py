import random

def rng_app(count=4, min_value=1, max_value=6):
    numbers = [random.randint(min_value, max_value) for _ in range(count)]
    print(f"Generated Numbers: {', '.join(map(str, numbers))}")

if __name__ == '__main__':
    rng_app()
