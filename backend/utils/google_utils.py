import os
import logging
import base64
import json
from typing import Optional

import google.auth
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

def get_credentials():
    """
    Simplified credential retrieval for stateless mode.
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
        if os.path.exists(creds_path):
            try:
                return service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading service account file at {creds_path}: {e}")
    
    # 4. Fallback search
    filename = "google-credentials.json"
    search_paths = [
        filename,
        os.path.join(os.getcwd(), filename),
        "/etc/secrets/" + filename
    ]
    
    for p in search_paths:
        if os.path.exists(p):
            try:
                return service_account.Credentials.from_service_account_file(p, scopes=scopes)
            except Exception as e:
                logger.error(f"Error loading fallback file at {p}: {e}")

    # 5. Default
    try:
        credentials, project = google.auth.default(scopes=scopes)
        return credentials
    except Exception:
        return None