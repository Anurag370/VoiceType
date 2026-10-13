# 🎙️ Voice Type

**Turn your speech into text, anywhere on Windows.**

Voice Type is a Windows desktop voice-typing application powered by Groq speech transcription. Use a global keyboard shortcut to record your voice, transcribe it, and automatically paste the resulting text into your active application.

## ✨ Features

- 🎤 Global recording shortcut: `Ctrl + Alt + Space`
- 🌊 Floating waveform indicator
- ☁️ Cloud transcription powered by Groq
- 📋 Automatic clipboard copy and paste
- 🔐 User-configured API key stored through Windows Credential Manager
- ⚙️ Settings to replace or remove your API key
- 🖥️ Packaged Windows desktop application

## 📥 Installation

1. Open the project's **GitHub Releases** page.
2. Download `VoiceType-0.1.0-Windows.zip`.
3. Extract the entire ZIP to a folder.
4. Run `VoiceType.exe`.
5. Enter your Groq API key when prompted.

You do not need to install Python to use a correctly packaged release.

### Requirements

- Windows 10 or Windows 11
- Internet connection
- A Groq account and API key

## 🔑 Configure your API key

1. Visit the [Groq Console](https://console.groq.com/keys).
2. Create an API key.
3. Enter it in Voice Type's setup window.
4. Use Settings to replace or remove the saved key later.

Voice Type uses your key to authorize transcription requests. Recorded audio is sent to Groq for cloud transcription.

**Never share your API key or commit it to GitHub.** The application stores the saved key using Windows Credential Manager.

## ⌨️ Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Alt + Space` | Start or stop recording |
| `Ctrl + Alt + S` | Open Settings |
| `Ctrl + Alt + Q` | Exit Voice Type |

## 🛠️ Run from source

Clone the repository:

```powershell
git clone YOUR_REPOSITORY_URL
cd voice-type
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

Run the application:

```powershell
python app.py
```

For local development, you can place `GROQ_API_KEY` in a `.env` file in the project root. Never commit your real `.env` file.

## 📦 Build the Windows application

Use the included PyInstaller specification:

```powershell
python -m PyInstaller --noconfirm --clean VoiceType.spec
```

The resulting application should be in:

```text
dist/VoiceType/
```

Distribute the complete output folder as a ZIP, not just `VoiceType.exe`.

## 🐛 Troubleshooting

**The application won't start**
- Extract all files from the ZIP.
- Check the log at `%APPDATA%\VoiceType\voicetype.log` if logging is configured.
- Try running a console-enabled build to inspect errors.

**The microphone doesn't work**
- Check Windows microphone privacy permissions.
- Verify your microphone works in other applications.

**Transcription fails**
- Check your internet connection.
- Verify your API key in Settings.
- Check your Groq account and API access.

**Text goes into the wrong application**
- Focus
