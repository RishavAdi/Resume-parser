import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv(encoding="utf-8-sig")

class Config:
    @staticmethod
    def get_api_key() -> str:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Please set it in .env file or environment variables"
            )
        return api_key

    # OpenRouter specific configs
    API_BASE = "https://openrouter.ai/api/v1"
    MODEL_NAME = "openai/gpt-oss-20b:free"  # OpenRouter model name
    MAX_TOKENS = 3000
    TEMPERATURE = 0.1
    SITE_URL = "http://localhost:8501"  # Your Streamlit app URL
    SITE_NAME = "ResumeParser"  # Your app name