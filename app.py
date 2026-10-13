import threading
import tkinter as tk
import queue

from pynput import keyboard

from audio import AudioRecorder
from transcriber import transcribe_audio
from clipboard import copy_text, paste_text
from popup import VoicePopup

from setup_dialog import ensure_api_key
from settings_dialog import show_settings


GREEN = "#4ADE80"
AMBER = "#FBBF24"
RED = "#F87171"


class VoiceTypeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        print("Voice Type: checking API configuration...")
        
        if not ensure_api_key(self.root):
            self.root.after(0, self.root.destroy)
            return

        print("Voice Type: API configuration ready.")
        
        self.recorder = AudioRecorder()
        self.popup = VoicePopup(self.root, lambda: self.recorder.level)

        self.state = "IDLE"
        self.error_reset_id = None
        self.closed = False
        self.ui_queue = queue.Queue()

        self.listener = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+<space>": self._schedule_toggle,
            "<ctrl>+<alt>+q": self._schedule_shutdown,
            "<ctrl>+<alt>+s": self._schedule_settings,
        })

        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        self.root.after(50, self.process_ui_queue)
        self.listener.start()

        print("Voice Type is running.")
        print("Ctrl + Alt + Space: start/stop recording")
        print("Ctrl + Alt + Q: quit")

    
    def _schedule_toggle(self):
        """Called by pynput; do not call Tkinter from this thread."""
        if not self.closed:
            self.ui_queue.put(("toggle", None))


    def _schedule_shutdown(self):
        """Request shutdown through the UI queue."""
        if not self.closed:
            self.ui_queue.put(("shutdown", None))


    def _schedule_settings(self):
        """Request the Settings window through the UI queue."""
        if not self.closed:
            self.ui_queue.put(("settings", None))



    def open_settings(self):
        if self.closed:
            return

        if self.state in ("LISTENING", "TRANSCRIBING", "DELIVERING"):
            print("Stop recording and wait for transcription before opening settings.")
            return

        show_settings(self.root)

    def set_state(self, state, message, color):
        self.state = state
        self.popup.set_state(state, message, color)

    def toggle_recording(self):
        if self.closed:
            return

        if self.state in ("TRANSCRIBING", "DELIVERING"):
            print("Please wait for the current transcription.")
            return

        if self.state == "IDLE":
            try:
                self.recorder.start()
                self.set_state(
                    "LISTENING", "● LISTENING", GREEN
                )
                print("Recording started.")
            except Exception as exc:
                self.show_error(f"Microphone error: {exc}")

        elif self.state == "LISTENING":
            try:
                audio = self.recorder.stop()
            except Exception as exc:
                self.show_error(f"Recording error: {exc}")
                return

            if audio is None:
                self.show_error("Recording was too short or empty.")
                return

            self.set_state(
                "TRANSCRIBING", "◌ TRANSCRIBING", AMBER
            )

            threading.Thread(
                target=self.transcription_worker,
                args=(audio,),
                daemon=True,
            ).start()

    
    def transcription_worker(self, audio):
        """Run transcription without interacting with Tkinter."""
        try:
            text = transcribe_audio(audio)

            if not text:
                raise RuntimeError("No speech was recognized.")

            self.ui_queue.put(("success", text))

        except Exception as exc:
            self.ui_queue.put(("error", str(exc)))


    def deliver(self, text):
        if self.closed:
            return

        try:
            copy_text(text)

            self.set_state(
                "DELIVERING", "PASTING TEXT", AMBER
            )

            self.popup.window.withdraw()

            self.root.after(
                200, lambda result=text: self.finish_paste(result)
            )

        except Exception as exc:
            self.show_error(f"Clipboard error: {exc}")

    def finish_paste(self, text):
        if self.closed:
            return

        try:
            paste_text()
            print("Transcription:", text)

            self.set_state(
                "SUCCESS", "✓ COPIED & PASTED", GREEN
            )

            self.root.after(1200, self.return_to_idle)

        except Exception as exc:
            self.show_error(
                f"Paste failed; text is on clipboard: {exc}"
            )

    
    def show_error(self, message):
        """Display an error and automatically restore the idle state."""
        if self.closed:
            return

        print("Voice Type error:", message)

        # Cancel any previous error-recovery timer.
        if self.error_reset_id is not None:
            try:
                self.root.after_cancel(self.error_reset_id)
            except tk.TclError:
                pass
            self.error_reset_id = None

        self.set_state("ERROR", "ERROR — SEE TERMINAL", RED)

        self.error_reset_id = self.root.after(
            3000,
            self.return_to_idle,
        )


    def return_to_idle(self):
        """Restore the app to IDLE after success or an error."""
        if self.closed:
            return

        self.error_reset_id = None
        self.set_state("IDLE", "", GREEN)



    def shutdown(self):
        """Stop background activity and destroy the UI safely."""
        if self.closed:
            return

        # Set this first so new events and callbacks are ignored.
        self.closed = True

        # Cancel the pending error-recovery callback if one exists.
        if self.error_reset_id is not None:
            try:
                self.root.after_cancel(self.error_reset_id)
            except tk.TclError:
                pass
            self.error_reset_id = None

        # Stop listening for global shortcuts.
        try:
            self.listener.stop()
        except Exception as exc:
            print(f"Warning: could not stop shortcut listener: {exc}")

        # Stop microphone capture if it is active.
        if self.recorder.recording:
            try:
                self.recorder.stop()
            except Exception as exc:
                print(f"Warning: could not stop microphone cleanly: {exc}")

        # Destroy the Tkinter root even if cleanup reported an error.
        try:
            self.root.destroy()
        except tk.TclError:
            pass

        
    
    def process_ui_queue(self):
        """Process queued events exclusively on Tkinter's main thread."""
        if self.closed:
            return

        try:
            while True:
                message_type, payload = self.ui_queue.get_nowait()

                if message_type == "toggle":
                    self.toggle_recording()

                elif message_type == "settings":
                    self.open_settings()

                elif message_type == "shutdown":
                    self.shutdown()
                    return

                elif message_type == "success":
                    self.deliver(payload)

                elif message_type == "error":
                    self.show_error(payload)

        except queue.Empty:
            pass

        if not self.closed:
            self.root.after(50, self.process_ui_queue)


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    VoiceTypeApp().run()
