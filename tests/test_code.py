# Simple Python test code for code analyzer
# This is a clean, well-written Python script with no issues

def greet(name):
    """Function to greet a person by name."""
    if not name:
        return "Hello, World!"
    return f"Hello, {name}!"

def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    if length <= 0 or width <= 0:
        raise ValueError("Length and width must be positive numbers")
    return length * width

def main():
    """Main function to demonstrate the code."""
    # Test greeting function
    print(greet("Alice"))
    print(greet(""))
    
    # Test area calculation
    try:
        area = calculate_area(5, 3)
        print(f"Area of rectangle: {area}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()