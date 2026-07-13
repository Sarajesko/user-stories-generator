import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


class ConfigurationError(Exception):
    pass


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(f"Missing required environment variable: {name}")
    return value


def get_database_url() -> str:
    return _require_env("DATABASE_URL")


@dataclass(frozen=True)
class AzureOpenAISettings:
    endpoint: str
    api_key: str
    api_version: str
    deployment: str
    temperature: float
    max_tokens: int
    top_p: float


def load_azure_settings() -> AzureOpenAISettings:
    endpoint = _require_env("AZURE_OPENAI_ENDPOINT").rstrip("/")
    return AzureOpenAISettings(
        endpoint=endpoint,
        api_key=_require_env("AZURE_OPENAI_API_KEY"),
        api_version=_require_env("AZURE_OPENAI_API_VERSION"),
        deployment=_require_env("AZURE_OPENAI_DEPLOYMENT"),
        temperature=float(os.getenv("TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
        top_p=float(os.getenv("TOP_P", "1.0")),
    )
