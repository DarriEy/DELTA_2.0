# backend/utils/google_utils.py
import os
import logging
import base64
import json
from typing import Optional

import google.auth
from google.oauth2 import service_account
from google.cloud import texttospeech
from google.cloud import storage
from google.cloud import vision
# import google.generativeai as genai  # Deprecated

from utils.config import get_settings

logger = logging.getLogger(__name__)

def get_credentials():
    """
    Centralized credential retrieval.
    1. Checks for GOOGLE_CREDENTIALS_JSON (Raw JSON string)
    2. Checks for GOOGLE_CREDENTIALS_BASE64
    3. Checks for valid JSON file path
    4. Falls back to default credentials
    """
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    # 1. Raw JSON string
    raw_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if raw_json:
        try:
            creds_dict = json.loads(raw_json)
            return service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
        except Exception as e:
            logger.error(f"Error parsing GOOGLE_CREDENTIALS_JSON: {e}")

    # 2. Base64 encoded JSON
    base64_creds = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
    if base64_creds:
        try:
            creds_json = base64.b64decode(base64_creds).decode("utf-8")
            creds_dict = json.loads(creds_json)
            return service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
        except Exception as e:
            logger.error(f"Error decoding GOOGLE_CREDENTIALS_BASE64: {e}")

    # 3. File path handling
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        # If it's a local path from another OS, ignore it immediately
        import platform
        is_foreign_path = creds_path.startswith("/Users/") and platform.system() != "Darwin"
        
        if is_foreign_path:
            logger.warning(f"Ignoring foreign credentials path: {creds_path}")
            # IMPORTANT: Temporary remove it from environ so google.auth.default doesn't try to use it
            # We use a context-local approach or just pop it if we know it's garbage
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
            creds_path = None # Reset for later checks
        elif os.path.exists(creds_path):
            try:
                return service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading service account file at {creds_path}: {e}")
    
    # 4. Search fallback paths if we don't have credentials yet
    # Use the original filename if provided, otherwise default
    filename = os.path.basename(creds_path) if creds_path else "google-credentials.json"
    search_paths = [
        filename,
        os.path.join(os.getcwd(), filename),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), filename),
        os.path.join(os.path.dirname(__file__), filename),
        "/app/" + filename,
        "/etc/secrets/" + filename
    ]
    
    for p in search_paths:
        if os.path.exists(p):
            try:
                logger.info(f"Found credentials file at {p}")
                # Set it so other libraries might find it too
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = p
                return service_account.Credentials.from_service_account_file(p, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading service account file at {p}: {e}")

    # 5. Default (only if env var is NOT a broken path)
    try:
        # Re-check env var before calling default
        current_env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if current_env_path and not os.path.exists(current_env_path):
            logger.warning(f"Clearing broken GOOGLE_APPLICATION_CREDENTIALS path: {current_env_path}")
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

        credentials, project = google.auth.default(scopes=scopes)
        return credentials
    except Exception as e:
        logger.error(f"Error getting default credentials: {e}")
        return None

def get_tts_client():
    try:
        creds = get_credentials()
        if creds:
            return texttospeech.TextToSpeechClient(credentials=creds)
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        logger.error(f"Failed to initialize TTS client: {e}")
        return None

def get_storage_client():
    creds = get_credentials()
    if creds:
        return storage.Client(credentials=creds, project=get_settings().project_id)
    return storage.Client()

def get_vision_client():

    creds = get_credentials()

    if creds:

        return vision.ImageAnnotatorClient(credentials=creds)

    return vision.ImageAnnotatorClient()
