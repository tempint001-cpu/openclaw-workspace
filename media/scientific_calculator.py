#!/usr/bin/env python3
"""
Scientific Calculator
Features: Basic math + Scientific functions
"""

import math

def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else "Error: Divide by zero"

def power(a, b): return a ** b
def sqrt(x): return math.sqrt(x) if x >= 0 else "Error: Negative number"
def sin(x): return math.sin(math.radians(x))
def cos(x): return math.cos(math.radians(x))
def tan(x): return math.tan(math.radians(x))

def log(x): return math.log(x) if x > 0 else "Error: Non-positive number"
def log10(x): return math.log10(x) if x > 0 else "Error: Non-positive number"
def factorial(x): return math.factorial(int(x)) if x >= 0 else "Error: Negative number"

def circle_area(r): return math.pi * r ** 2
def circle_circumference(r): return 2 * math.pi * r

def main():
    print("\n🧮 Scientific Calculator 🧮")
    print("=" * 35)
    print("Operations:")
    print("  +  -  *  /  = Basic")
    print("  ^  = Power (e.g., 2^3 = 8)")
    print("  sqrt = Square root")
    print("  sin/cos/tan = Trig (degrees)")
    print("  log = Natural log")
    print("  log10 = Base-10 log")
    print("  fact = Factorial")
    print("  area = Circle area")
    print("  circum = Circle circumference")
    print("  q = Quit")
    print("=" * 35)
    
    while True:
        op = input("\nEnter operation: ").strip().lower()
        
        if op == 'q':
            print("👋 Bye!")
            break
        
        try:
            if op in ['+', '-', '*', '/', '^']:
                a = float(input("  Enter first number: "))
                b = float(input("  Enter second number: "))
                if op == '+': print(f"  Result: {add(a, b)}")
                elif op == '-': print(f"  Result: {subtract(a, b)}")
                elif op == '*': print(f"  Result: {multiply(a, b)}")
                elif op == '/': print(f"  Result: {divide(a, b)}")
                elif op == '^': print(f"  Result: {power(a, b)}")
            
            elif op == 'sqrt':
                x = float(input("  Enter number: "))
                print(f"  Result: {sqrt(x):.4f}")
            
            elif op in ['sin', 'cos', 'tan']:
                x = float(input("  Enter angle (degrees): "))
                if op == 'sin': print(f"  Result: {sin(x):.4f}")
                elif op == 'cos': print(f"  Result: {cos(x):.4f}")
                elif op == 'tan': print(f"  Result: {tan(x):.4f}")
            
            elif op == 'log':
                x = float(input("  Enter number: "))
                print(f"  Result: {log(x):.4f}")
            
            elif op == 'log10':
                x = float(input("  Enter number: "))
                print(f"  Result: {log10(x):.4f}")
            
            elif op == 'fact':
                x = float(input("  Enter number: "))
                print(f"  Result: {factorial(x)}")
            
            elif op == 'area':
                r = float(input("  Enter radius: "))
                print(f"  Result: {circle_area(r):.4f}")
            
            elif op == 'circum':
                r = float(input("  Enter radius: "))
                print(f"  Result: {circle_circumference(r):.4f}")
            
            else:
                print("  ❌ Unknown operation!")
        
        except ValueError:
            print("  ❌ Invalid input!")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    main()