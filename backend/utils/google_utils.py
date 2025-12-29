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

from utils.config import config

logger = logging.getLogger(__name__)

def get_credentials():
    """
    Centralized credential retrieval.
    1. Checks for GOOGLE_CREDENTIALS_BASE64
    2. Checks for JSON file path
    3. Falls back to default credentials
    """
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    # 1. Base64 encoded JSON
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
        # Check absolute or relative to CWD
        if os.path.exists(creds_path):
            try:
                return service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading service account file at {creds_path}: {e}")
        
        # Fallback: check if it's relative to the backend directory if CWD is project root
        alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.basename(creds_path))
        if os.path.exists(alt_path):
            try:
                return service_account.Credentials.from_service_account_file(alt_path, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading service account file at {alt_path}: {e}")

    
    # 3. Default
    try:
        credentials, project = google.auth.default(scopes=scopes)
        return credentials
    except Exception as e:
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
        return storage.Client(credentials=creds, project=config.get("PROJECT_ID"))
    return storage.Client()

def get_vision_client():

    creds = get_credentials()

    if creds:

        return vision.ImageAnnotatorClient(credentials=creds)

    return vision.ImageAnnotatorClient()
