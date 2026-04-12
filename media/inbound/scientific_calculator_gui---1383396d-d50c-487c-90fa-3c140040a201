#!/usr/bin/env python3
"""
Scientific Calculator with GUI (Tkinter)
"""

import math
from tkinter import *

def on_click(key):
    """Handle button clicks"""
    if key == 'C':
        display.set('')
    elif key == '=':
        try:
            expr = display.get().replace('^', '**').replace('sqrt', 'math.sqrt').replace('sin', 'math.sin(math.radians').replace('cos', 'math.cos(math.radians').replace('tan', 'math.tan(math.radians')
            # Handle closing parens for trig
            if 'math.sin(math.radians' in expr:
                expr += ')'
            elif 'math.cos(math.radians' in expr:
                expr += ')'
            elif 'math.tan(math.radians' in expr:
                expr += ')'
            result = eval(expr)
            display.set(str(result))
        except Exception as e:
            display.set('Error')
    else:
        display.set(display.get() + key)

root = Tk()
root.title("🧮 Scientific Calculator")
root.geometry("350x450")
root.configure(bg="#1e1e1e")

display = StringVar()

# Display
Label(root, textvariable=display, bg="#1e1e1e", fg="white", font=("Arial", 24), anchor="e", padx=10).pack(fill=BOTH, pady=5, padx=5)

# Buttons
buttons = [
    ('(', ')', '^', 'C'),
    ('7', '8', '9', '/'),
    ('4', '5', '6', '*'),
    ('1', '2', '3', '-'),
    ('0', '.', '=', '+'),
    ('sqrt', 'sin', 'cos', 'tan'),
]

for row in buttons:
    frame = Frame(root, bg="#1e1e1e")
    frame.pack(expand=True, fill=BOTH)
    for btn in row:
        Button(frame, text=btn, font=("Arial", 18), bg="#2d2d2d", fg="white", 
              command=lambda b=btn: on_click(b)).pack(side=LEFT, expand=True, fill=BOTH, padx=2, pady=2)

root.mainloop()