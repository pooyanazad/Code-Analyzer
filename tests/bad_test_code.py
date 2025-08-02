# Intentionally problematic Python code for testing code analyzer
# This file contains multiple issues for testing purposes

import os
import subprocess
import pickle
from random import *

# Global variables (bad practice)
global_var = None
password = "admin123"  # Hardcoded password (security issue)
api_key = "sk-1234567890abcdef"  # Exposed API key

def unsafe_function(user_input):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    
    # Command injection vulnerability
    os.system("ls " + user_input)
    
    # Eval vulnerability
    result = eval(user_input)
    
    return result

def inefficient_function(data):
    # Inefficient nested loops
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            for k in range(len(data)):
                if data[i] == data[j]:
                    result.append(data[k])
    return result

def bad_exception_handling():
    try:
        x = 1/0
    except:
        pass  # Silent exception handling

def unused_variables():
    x = 10
    y = 20
    z = 30
    return x  # y and z are unused

class BadClass:
    def __init__(self):
        pass
    
    def method_with_no_self(self):
        global global_var
        global_var = "modified"
    
    def duplicate_method(self):
        return "first"
    
    def duplicate_method(self):  # Duplicate method name
        return "second"

def file_operations():
    # File operations without proper error handling
    f = open("nonexistent.txt", "r")
    content = f.read()
    # File not closed properly
    
    # Unsafe pickle loading
    with open("data.pkl", "rb") as file:
        data = pickle.load(file)  # Unsafe deserialization

def memory_leak():
    # Potential memory leak
    big_list = []
    while True:
        big_list.append(list(range(1000)))
        if len(big_list) > 100:
            break
    return big_list

def poor_naming():
    a = 10
    b = 20
    c = a + b
    return c

def long_function_with_many_parameters(param1, param2, param3, param4, param5, param6, param7, param8, param9, param10):
    # Function with too many parameters
    if param1 and param2 and param3 and param4 and param5:
        if param6 or param7 or param8 or param9 or param10:
            return param1 + param2 + param3
    return 0

def main():
    # Missing docstring
    user_data = input("Enter data: ")
    unsafe_function(user_data)
    
    # Hardcoded values
    data = [1, 2, 3, 4, 5] * 1000
    inefficient_function(data)
    
    # Unused import
    import json
    
    # Magic numbers
    result = user_data * 42 + 3.14159
    
    # No return statement

# Missing if __name__ == "__main__" guard
main()

# Unreachable code
print("This will never execute")

# Syntax error (missing closing parenthesis)
# print("Hello world"