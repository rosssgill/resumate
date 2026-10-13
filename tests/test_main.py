import json

from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_compile_writes_pdf_next_to_input(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(json.dumps({"basics": {"name": "Jane Doe"}}))

    result = runner.invoke(app, [str(resume_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "cv.pdf").read_bytes().startswith(b"%PDF")


def test_compile_writes_pdf_to_output_path(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text("{}")
    output_path = tmp_path / "out" / "resume.pdf"

    result = runner.invoke(app, [str(resume_path), "--output", str(output_path)])

    assert result.exit_code == 0, result.output
    assert output_path.read_bytes().startswith(b"%PDF")


def test_compile_reports_invalid_resume(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(json.dumps({"work": [{"startDate": "April 2023"}]}))

    result = runner.invoke(app, [str(resume_path)])

    assert result.exit_code == 1
    assert "work.0.startDate" in result.output
    assert not (tmp_path / "cv.pdf").exists()


def test_compile_rejects_missing_file(tmp_path):
    result = runner.invoke(app, [str(tmp_path / "missing.json")])

    assert result.exit_code == 2


def test_compile_reads_non_ascii_utf8(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_text(
        json.dumps({"basics": {"name": "Zoë Ångström"}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = runner.invoke(app, [str(resume_path)])

    assert result.exit_code == 0, result.output


def test_compile_reports_non_utf8_file(tmp_path):
    resume_path = tmp_path / "cv.json"
    resume_path.write_bytes('{"basics": {"name": "Zoë"}}'.encode("latin-1"))

    result = runner.invoke(app, [str(resume_path)])

    assert result.exit_code == 1
    assert "UTF-8" in result.output
