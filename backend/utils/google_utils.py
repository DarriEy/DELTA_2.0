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
    3. Checks for JSON file path
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

    # 2. File path
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        # Check if it's a local-only path (e.g. starting with /Users/ on a non-macOS system)
        import platform
        is_local_path = creds_path.startswith("/Users/") and platform.system() != "Darwin"
        
        if not is_local_path and os.path.exists(creds_path):
            try:
                return service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading service account file at {creds_path}: {e}")
        
        if is_local_path:
            logger.warning(f"Ignoring local-only credentials path: {creds_path}")
        
        # Check if it's just a filename and might be in the same dir as this script
        # or in the backend root
        filename = os.path.basename(creds_path)
        search_paths = [
            filename,
            os.path.join(os.getcwd(), filename),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), filename),
            os.path.join(os.path.dirname(__file__), filename),
            "/app/" + filename,
            "/etc/secrets/" + filename # Render secrets path
        ]
        
        for p in search_paths:
            if os.path.exists(p):
                try:
                    logger.info(f"Found credentials file at {p}")
                    return service_account.Credentials.from_service_account_file(p, scopes=scopes)
                except Exception as e:
                    logger.error(f"Error loading service account file at {p}: {e}")

    
    # 3. Default
    try:
        credentials, project = google.auth.default(scopes=scopes)
        return credentials
    except Exception as e:
        # If we have a path set that didn't exist, we probably shouldn't try default 
        # because it might be a broken local path that's making it fail.
        if not creds_path:
            logger.error(f"Error getting default credentials: {e}")
        return None

def get_tts_client():
    creds = get_credentials()
    if creds:
        return texttospeech.TextToSpeechClient(credentials=creds)
    return texttospeech.TextToSpeechClient()

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
