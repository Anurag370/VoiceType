import os

import keyring
from dotenv import load_dotenv

# Used by Windows Credential Manager to identify this application's secret.
SERVICE_NAME = "VoiceType"
API_KEY_NAME = "groq_api_key"

load_dotenv()


def get_api_key() -> str | None:
    try:
        saved_key = keyring.get_password(
            SERVICE_NAME,
            API_KEY_NAME,
        )
    except Exception as exc:
        raise RuntimeError(
            "Could not access Windows Credential Manager."
        ) from exc

    if saved_key and saved_key.strip():
        return saved_key.strip()

    env_key = os.getenv("GROQ_API_KEY")
    return env_key.strip() if env_key and env_key.strip() else None


def save_api_key(api_key: str) -> None:
    api_key = api_key.strip()

    if not api_key:
        raise ValueError("The Groq API key cannot be empty.")

    try:
        keyring.set_password(
            SERVICE_NAME,
            API_KEY_NAME,
            api_key,
        )
    except Exception as exc:
        raise RuntimeError(
            "Could not save the API key to Windows Credential Manager."
        ) from exc


def delete_api_key() -> None:
    try:
        keyring.delete_password(
            SERVICE_NAME,
            API_KEY_NAME,
        )
    except keyring.errors.PasswordDeleteError:
        pass
    except Exception as exc:
        raise RuntimeError(
            "Could not remove the saved API key."
        ) from exc

def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Check whether the supplied key can authenticate with Groq."""
    from groq import Groq

    api_key = api_key.strip()

    if not api_key:
        return False, "Please enter your Groq API key."

    try:
        client = Groq(
            api_key=api_key,
            timeout=10.0,
            max_retries=0,
        )

        client.models.list()

        return True, "API key verified successfully."

    except Exception as exc:
        status_code = getattr(exc, "status_code", None)

        if status_code == 401:
            return False, "The API key was rejected. Check the key and try again."

        if status_code == 403:
            return False, "Access was denied. Check your Groq account and permissions."

        if status_code == 429:
            return False, "Groq rate limit reached. Please try again later."

        if status_code is not None and status_code >= 500:
            return False, "Groq is temporarily unavailable. Try again later."

        return False, (
            "Could not verify the key. Check your internet connection "
            "and try again."
        )
