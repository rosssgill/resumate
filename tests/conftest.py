import os

import pytest


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    """Keep the developer's .env and RESUMATE_* variables out of tests, and stop
    variables loaded from a .env in one test leaking into the next."""
    environ = {k: v for k, v in os.environ.items() if not k.startswith("RESUMATE_")}
    monkeypatch.setattr(os, "environ", environ)
    monkeypatch.chdir(tmp_path)
