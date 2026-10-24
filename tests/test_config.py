import os

import pytest
from pydantic import ValidationError

from core import config
from core.config import Paper, Settings, load_env_files


def test_defaults():
    settings = Settings()

    assert settings.model is None
    assert settings.paper == Paper.A4
    assert settings.max_pages == 1
    assert settings.min_font_size < settings.default_font_size


def test_reads_prefixed_environment_variables(monkeypatch):
    monkeypatch.setenv("RESUMATE_PAPER", "us-letter")
    monkeypatch.setenv("RESUMATE_MAX_PAGES", "2")

    settings = Settings()

    assert settings.paper == Paper.US_LETTER
    assert settings.max_pages == 2


def test_explicit_values_override_environment(monkeypatch):
    monkeypatch.setenv("RESUMATE_PAPER", "us-letter")

    assert Settings(paper=Paper.A4).paper == Paper.A4


@pytest.mark.parametrize(
    "values",
    [
        {"max_pages": 0},
        {"font_size_step": 0},
        {"min_font_size": 12, "default_font_size": 11},
    ],
)
def test_rejects_invalid_values(values):
    with pytest.raises(ValidationError):
        Settings(**values)


def test_load_env_files_reads_project_then_user_file(tmp_path, monkeypatch):
    user_env = tmp_path / "user.env"
    user_env.write_text("RESUMATE_MODEL=user-model\nANTHROPIC_API_KEY=user-key\n")
    (tmp_path / ".env").write_text("RESUMATE_MODEL=project-model\n")
    monkeypatch.setattr(config, "USER_ENV_FILE", user_env)
    monkeypatch.chdir(tmp_path)

    load_env_files()

    assert os.environ["RESUMATE_MODEL"] == "project-model"
    assert os.environ["ANTHROPIC_API_KEY"] == "user-key"


def test_load_env_files_keeps_existing_environment(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("RESUMATE_MODEL=project-model\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RESUMATE_MODEL", "real-model")

    load_env_files()

    assert os.environ["RESUMATE_MODEL"] == "real-model"
