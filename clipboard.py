import pyautogui
import pyperclip


def copy_text(text: str) -> None:
    if text and text.strip():
        pyperclip.copy(text)


def paste_text() -> None:
    pyautogui.hotkey("ctrl", "v")
