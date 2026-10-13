
import tkinter as tk

from config import get_api_key, save_api_key, validate_api_key


def ensure_api_key(root: tk.Tk) -> bool:
    """Show first-run setup if no API key is configured."""

    if get_api_key():
        return True

    result = {"configured": False}

    dialog = tk.Toplevel(root)
    dialog.title("Voice Type Setup")
    dialog.geometry("440x300")
    dialog.resizable(False, False)
    dialog.configure(bg="#111827")
    # Show the setup window even though the main root is hidden.
    dialog.attributes("-topmost", True)
    dialog.deiconify()
    dialog.lift()
    dialog.focus_force()
    dialog.grab_set()

    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 440) // 2
    y = (dialog.winfo_screenheight() - 300) // 2
    dialog.geometry(f"440x300+{x}+{y}")

    dialog.attributes("-topmost", True)
    dialog.deiconify()
    dialog.lift()
    dialog.focus_force()
    dialog.grab_set()

    def close_dialog():
        result["configured"] = False
        dialog.destroy()

    dialog.protocol("WM_DELETE_WINDOW", close_dialog)

    tk.Label(
        dialog,
        text="Welcome to Voice Type",
        font=("Segoe UI", 18, "bold"),
        fg="#F9FAFB",
        bg="#111827",
    ).pack(pady=(22, 6))

    tk.Label(
        dialog,
        text="Enter your Groq API key to get started.",
        font=("Segoe UI", 10),
        fg="#D1D5DB",
        bg="#111827",
    ).pack(pady=(0, 12))

    key_entry = tk.Entry(
        dialog,
        width=43,
        show="*",
        font=("Segoe UI", 10),
        relief="flat",
    )
    key_entry.pack(ipady=7, padx=24)
    key_entry.focus_set()

    show_key = tk.BooleanVar(value=False)

    def toggle_key_visibility():
        key_entry.configure(show="" if show_key.get() else "*")

    tk.Checkbutton(
        dialog,
        text="Show API key",
        variable=show_key,
        command=toggle_key_visibility,
        fg="#D1D5DB",
        bg="#111827",
        activebackground="#111827",
        activeforeground="#F9FAFB",
        selectcolor="#1F2937",
    ).pack(anchor="w", padx=30, pady=(5, 0))

    status = tk.Label(
        dialog,
        text="Your key will be stored in Windows Credential Manager.",
        wraplength=390,
        font=("Segoe UI", 9),
        fg="#9CA3AF",
        bg="#111827",
    )
    status.pack(pady=(8, 5))

    save_button = tk.Button(
        dialog,
        text="Verify and Save",
        font=("Segoe UI", 10, "bold"),
        bg="#4ADE80",
        fg="#111827",
        activebackground="#86EFAC",
        relief="flat",
        cursor="hand2",
    )
    save_button.pack(ipadx=16, ipady=5, pady=(4, 0))

    def save_key():
        api_key = key_entry.get().strip()

        if not api_key:
            status.configure(
                text="Please enter your Groq API key.",
                fg="#F87171",
            )
            return

        save_button.configure(state="disabled")
        key_entry.configure(state="disabled")
        status.configure(
            text="Verifying your API key...",
            fg="#FBBF24",
        )
        dialog.update_idletasks()

        try:
            valid, message = validate_api_key(api_key)

            if not valid:
                status.configure(text=message, fg="#F87171")
                return

            save_api_key(api_key)
            result["configured"] = True
            status.configure(
                text="API key saved. Voice Type is ready!",
                fg="#4ADE80",
            )
            dialog.after(700, dialog.destroy)

        except Exception as exc:
            status.configure(
                text=f"Could not save the API key: {exc}",
                fg="#F87171",
            )

        finally:
            if dialog.winfo_exists():
                save_button.configure(state="normal")
                key_entry.configure(state="normal")

    save_button.configure(command=save_key)

    dialog.bind("<Return>", lambda _event: save_key())

    root.wait_window(dialog)

    return result["configured"]
