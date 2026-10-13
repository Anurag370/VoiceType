
import tkinter as tk
from tkinter import messagebox

from config import (
    delete_api_key,
    get_api_key,
    save_api_key,
    validate_api_key,
)


def show_settings(root: tk.Tk) -> None:
    """Open the Voice Type API-key settings window."""

    window = tk.Toplevel(root)
    window.title("Voice Type Settings")
    window.geometry("440x310")
    window.resizable(False, False)
    window.configure(bg="#111827")
    window.attributes("-topmost", True)

    # Position the window near the center of the screen.
    window.update_idletasks()
    x = (window.winfo_screenwidth() - 440) // 2
    y = (window.winfo_screenheight() - 310) // 2
    window.geometry(f"440x310+{x}+{y}")
    window.deiconify()
    window.lift()
    window.focus_force()

    tk.Label(
        window,
        text="Voice Type Settings",
        font=("Segoe UI", 18, "bold"),
        fg="#F9FAFB",
        bg="#111827",
    ).pack(pady=(20, 6))

    configured = bool(get_api_key())

    current_status = tk.Label(
        window,
        text=(
            "API key is configured."
            if configured
            else "No API key is configured."
        ),
        font=("Segoe UI", 10),
        fg="#4ADE80" if configured else "#FBBF24",
        bg="#111827",
    )
    current_status.pack(pady=(0, 12))

    tk.Label(
        window,
        text="Enter a new Groq API key to replace the current one:",
        font=("Segoe UI", 9),
        fg="#D1D5DB",
        bg="#111827",
    ).pack()

    key_entry = tk.Entry(
        window,
        width=46,
        show="*",
        font=("Segoe UI", 10),
        relief="flat",
    )
    key_entry.pack(ipady=6, padx=24, pady=(8, 4))

    show_key = tk.BooleanVar(value=False)

    def toggle_visibility():
        key_entry.configure(show="" if show_key.get() else "*")

    tk.Checkbutton(
        window,
        text="Show API key",
        variable=show_key,
        command=toggle_visibility,
        fg="#D1D5DB",
        bg="#111827",
        activebackground="#111827",
        activeforeground="#F9FAFB",
        selectcolor="#1F2937",
    ).pack(anchor="w", padx=28)

    status = tk.Label(
        window,
        text="Your key is stored locally in Windows Credential Manager.",
        wraplength=400,
        font=("Segoe UI", 9),
        fg="#9CA3AF",
        bg="#111827",
    )
    status.pack(pady=(5, 8))

    buttons = tk.Frame(window, bg="#111827")
    buttons.pack(pady=(0, 12))

    save_button = tk.Button(
        buttons,
        text="Verify and Save",
        bg="#4ADE80",
        fg="#111827",
        relief="flat",
        cursor="hand2",
    )
    save_button.pack(side="left", padx=5, ipadx=8, ipady=4)

    def save_new_key():
        api_key = key_entry.get().strip()

        if not api_key:
            status.configure(
                text="Enter an API key first.",
                fg="#F87171",
            )
            return

        save_button.configure(state="disabled")
        status.configure(
            text="Verifying API key...",
            fg="#FBBF24",
        )
        window.update_idletasks()

        try:
            valid, message = validate_api_key(api_key)

            if not valid:
                status.configure(text=message, fg="#F87171")
                return

            save_api_key(api_key)
            current_status.configure(
                text="API key is configured.",
                fg="#4ADE80",
            )
            key_entry.delete(0, tk.END)
            status.configure(
                text="New API key saved successfully.",
                fg="#4ADE80",
            )

        except Exception as exc:
            status.configure(
                text=f"Could not save API key: {exc}",
                fg="#F87171",
            )

        finally:
            if window.winfo_exists():
                save_button.configure(state="normal")

    save_button.configure(command=save_new_key)

    def remove_key():
        confirmed = messagebox.askyesno(
            "Remove API key",
            "Remove the saved Groq API key? "
            "Transcription will stop working until a key is configured.",
            parent=window,
        )

        if not confirmed:
            return

        try:
            delete_api_key()
            current_status.configure(
                text="Saved API key removed.",
                fg="#FBBF24",
            )
            status.configure(
                text="Configure a key again to use transcription.",
                fg="#FBBF24",
            )
        except Exception as exc:
            status.configure(
                text=f"Could not remove API key: {exc}",
                fg="#F87171",
            )

    tk.Button(
        buttons,
        text="Remove Key",
        command=remove_key,
        bg="#374151",
        fg="#F9FAFB",
        relief="flat",
        cursor="hand2",
    ).pack(side="left", padx=5, ipadx=8, ipady=4)

    tk.Button(
        buttons,
        text="Close",
        command=window.destroy,
        bg="#374151",
        fg="#F9FAFB",
        relief="flat",
        cursor="hand2",
    ).pack(side="left", padx=5, ipadx=8, ipady=4)
