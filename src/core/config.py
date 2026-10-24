from enum import StrEnum
from pathlib import Path
from typing import Self

import typer
from dotenv import load_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

USER_ENV_FILE = Path(typer.get_app_dir("resumate")) / ".env"


class Paper(StrEnum):
    A4 = "a4"
    US_LETTER = "us-letter"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RESUMATE_")

    model: str | None = None
    paper: Paper = Paper.A4
    max_pages: int = Field(default=1, ge=1)
    default_font_size: float = Field(default=11.0, gt=0)
    min_font_size: float = Field(default=10.0, gt=0)
    font_size_step: float = Field(default=0.25, gt=0)

    @model_validator(mode="after")
    def _check_font_sizes(self) -> Self:
        if self.min_font_size > self.default_font_size:
            raise ValueError("min_font_size must not exceed default_font_size")
        return self


def load_env_files() -> None:
    """Load ./.env, then the user .env, without overriding existing variables."""
    # Exported rather than read into Settings so pydantic-ai finds provider API keys
    load_dotenv(Path(".env"))
    load_dotenv(USER_ENV_FILE)
