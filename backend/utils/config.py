# backend/utils/config.py
from dataclasses import dataclass
from typing import List, Optional

from utils.settings import get_env

_SETTINGS = None


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: Optional[str]
    google_api_key: Optional[str]
    project_id: Optional[str]
    location: str
    google_application_credentials: Optional[str]

    llm_model: str
    image_model: str
    
    # New streaming API settings
    huggingface_api_key: Optional[str]
    elevenlabs_api_key: Optional[str]
    llm_provider: str
    tts_provider: str
    elevenlabs_voice_id: str

    hydro_model_base_url: str
    symfluence_code_dir: Optional[str]
    symfluence_data_dir: Optional[str]

    allowed_origins: List[str]

    jwt_secret_key: str
    jwt_algorithm: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            anthropic_api_key=get_env("ANTHROPIC_API_KEY"),
            google_api_key=get_env("GOOGLE_API_KEY"),
            project_id=get_env("PROJECT_ID"),
            location=get_env("LOCATION", "us-central1"),
            google_application_credentials=get_env("GOOGLE_APPLICATION_CREDENTIALS"),
            llm_model=get_env("LLM_MODEL", "gemini-2.0-flash"),
            image_model="imagen-3",
            # New streaming settings
            huggingface_api_key=get_env("HUGGINGFACE_API_KEY"),
            elevenlabs_api_key=get_env("ELEVENLABS_API_KEY"),
            llm_provider=get_env("LLM_PROVIDER", "gemini"),
            tts_provider=get_env("TTS_PROVIDER", "google"),
            elevenlabs_voice_id=get_env("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
            hydro_model_base_url=get_env("HYDRO_MODEL_BASE_URL", "http://localhost:8080"),
            symfluence_code_dir=get_env(
                "SYMFLUENCE_CODE_DIR",
                "/Users/darrieythorsson/compHydro/code/SYMFLUENCE",
            ),
            symfluence_data_dir=get_env(
                "SYMFLUENCE_DATA_DIR",
                "/Users/darrieythorsson/compHydro/data/SYMFLUENCE_data",
            ),
            allowed_origins=get_env(
                "ALLOWED_ORIGINS",
                ",".join(
                    [
                        "https://delta-backend-zom0.onrender.com",
                        "https://darriey.github.io",
                        "https://DarriEy.github.io",
                        "http://localhost:5173",
                        "http://localhost:4173",
                        "http://localhost:3000",
                        "http://localhost:3001",
                        "http://localhost:14525",
                    ]
                ),
            ).split(","),
            jwt_secret_key=get_env("JWT_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"),
            jwt_algorithm=get_env("JWT_ALGORITHM", "HS256"),
        )


def get_settings() -> Settings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings.from_env()
    return _SETTINGS


def reset_settings_for_tests() -> None:
    global _SETTINGS
    _SETTINGS = None
