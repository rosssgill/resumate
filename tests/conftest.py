import os

import pytest

from core import config


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    """Keep the developer's .env files and RESUMATE_* variables out of tests, and
    stop variables loaded from .env files in one test leaking into the next."""
    environ = {k: v for k, v in os.environ.items() if not k.startswith("RESUMATE_")}
    monkeypatch.setattr(os, "environ", environ)
    monkeypatch.setattr(config, "USER_ENV_FILE", tmp_path / "missing-user.env")
    monkeypatch.chdir(tmp_path)
