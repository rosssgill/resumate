import json

import httpx
from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_compile_writes_pdf_next_to_input(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(json.dumps({"basics": {"name": "Jane Doe"}}))

    result = runner.invoke(app, ["compile", str(resume_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "cv.pdf").read_bytes().startswith(b"%PDF")


def test_compile_writes_pdf_to_output_path(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")
    output_path = tmp_path / "out" / "resume.pdf"

    result = runner.invoke(
        app, ["compile", str(resume_path), "--output", str(output_path)]
    )

    assert result.exit_code == 0, result.output
    assert output_path.read_bytes().startswith(b"%PDF")


def test_compile_reports_invalid_resume(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(json.dumps({"work": [{"startDate": "April 2023"}]}))

    result = runner.invoke(app, ["compile", str(resume_path)])

    assert result.exit_code == 1
    assert "work.0.startDate" in result.output
    assert not (tmp_path / "cv.pdf").exists()


def test_compile_rejects_missing_file(tmp_path):
    result = runner.invoke(app, ["compile", str(tmp_path / "missing.json")])

    assert result.exit_code == 2


def test_compile_reads_non_ascii_utf8(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(
        json.dumps({"basics": {"name": "Zoë Ångström"}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["compile", str(resume_path)])

    assert result.exit_code == 0, result.output


def test_compile_reports_non_utf8_file(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_bytes('{"basics": {"name": "Zoë"}}'.encode("latin-1"))

    result = runner.invoke(app, ["compile", str(resume_path)])

    assert result.exit_code == 1
    assert "UTF-8" in result.output


def long_resume(bullets: int) -> str:
    bullet = "Delivered a meaningful improvement to a system that mattered a lot."
    return json.dumps({"work": [{"name": "Acme", "highlights": [bullet] * bullets}]})


def test_compile_warns_when_resume_overflows_page_limit(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(long_resume(200))

    result = runner.invoke(app, ["compile", str(resume_path)])

    assert result.exit_code == 0, result.output
    assert "exceeds the 1 page limit" in result.output
    assert (tmp_path / "cv.pdf").exists()


def test_compile_accepts_larger_page_limit(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(long_resume(60))

    result = runner.invoke(app, ["compile", str(resume_path), "--max-pages", "3"])

    assert result.exit_code == 0, result.output
    assert "exceeds" not in result.output


def test_compile_uses_requested_paper(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")

    result = runner.invoke(app, ["compile", str(resume_path), "--paper", "us-letter"])

    assert result.exit_code == 0, result.output
    assert b"612 792" in (tmp_path / "cv.pdf").read_bytes()


def test_coach_requires_a_model(tmp_path, monkeypatch):
    monkeypatch.delenv("RESUMATE_MODEL", raising=False)
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")

    result = runner.invoke(app, ["coach", str(resume_path)])

    assert result.exit_code == 1
    assert "RESUMATE_MODEL" in result.output


def test_coach_prints_feedback(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")

    result = runner.invoke(app, ["coach", str(resume_path), "--model", "test"])

    assert result.exit_code == 0, result.output
    assert "Summary" in result.output


def test_coach_reads_model_from_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("RESUMATE_MODEL", "test")
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")

    result = runner.invoke(app, ["coach", str(resume_path)])

    assert result.exit_code == 0, result.output


def test_coach_reads_job_file(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")
    job_path = tmp_path / "job.txt"
    job_path.write_text("Senior Go engineer")

    result = runner.invoke(
        app, ["coach", str(resume_path), "--model", "test", "--job", str(job_path)]
    )

    assert result.exit_code == 0, result.output


def test_coach_reports_unknown_model(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")

    result = runner.invoke(app, ["coach", str(resume_path), "--model", "nope:model"])

    assert result.exit_code == 1
    assert "Unknown model" in result.output


def test_coach_reports_unreachable_job_url(tmp_path, monkeypatch):
    def fake_get(url: str, **_) -> httpx.Response:
        return httpx.Response(403, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")

    result = runner.invoke(
        app,
        ["coach", str(resume_path), "--model", "test", "--job", "https://x.test/1"],
    )

    assert result.exit_code == 1
    assert "403" in result.output
