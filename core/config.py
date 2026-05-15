import os
from dotenv import load_dotenv

load_dotenv()


def get_serper_api_key() -> str:
    key = os.getenv("SERPER_API_KEY", "")
    if not key:
        raise ValueError("SERPER_API_KEY is not set in .env")
    return key


def get_groq_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY is not set in .env")
    return key
