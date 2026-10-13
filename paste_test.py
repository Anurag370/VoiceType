import time

import pyautogui
import pyperclip

text = "Hello from my Voice Type automation!"

pyperclip.copy(text)

print("Switch to Notepad within 3 seconds...")

time.sleep(3)

pyautogui.hotkey("ctrl", "v")

print("Paste shortcut sent.")