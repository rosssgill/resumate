import httpx
import pytest
from pydantic_ai import ModelMessage, ModelResponse, ToolCallPart, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from coach import Feedback, coach, load_job
from models import Resume

RESUME = Resume.model_validate({"basics": {"name": "Jane Doe"}})
FEEDBACK = {
    "summary": "Solid, but vague.",
    "suggestions": [
        {"path": "work.0.highlights.0", "issue": "Vague", "rewrite": "Cut CI time"}
    ],
}


def capturing_model(prompts: list[str]) -> FunctionModel:
    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        prompts.extend(
            str(part.content)
            for part in messages[-1].parts
            if isinstance(part, UserPromptPart)
        )
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, FEEDBACK)])

    return FunctionModel(respond)


def test_coach_returns_structured_feedback():
    feedback = coach(RESUME, model=TestModel())

    assert isinstance(feedback, Feedback)


def test_coach_sends_resume_and_job_to_model():
    prompts: list[str] = []

    feedback = coach(RESUME, model=capturing_model(prompts), job="Senior Go engineer")

    assert feedback.suggestions[0].path == "work.0.highlights.0"
    assert "Jane Doe" in prompts[0]
    assert "Senior Go engineer" in prompts[0]


def test_coach_omits_job_section_without_job():
    prompts: list[str] = []

    coach(RESUME, model=capturing_model(prompts))

    assert "job posting" not in prompts[0].lower()


def test_load_job_reads_file(tmp_path):
    job_path = tmp_path / "job.txt"
    job_path.write_text("Senior Go engineer", encoding="utf-8")

    assert load_job(str(job_path)) == "Senior Go engineer"


def test_load_job_fetches_url_as_text(monkeypatch):
    html = (
        "<html><head><style>p {}</style><script>track()</script></head>"
        "<body><h1>Senior Go engineer</h1><p>Remote, UK</p></body></html>"
    )

    def fake_get(url: str, **_) -> httpx.Response:
        return httpx.Response(200, text=html, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)

    text = load_job("https://jobs.example.com/123")

    assert "Senior Go engineer" in text
    assert "Remote, UK" in text
    assert "track()" not in text
    assert "p {}" not in text


def test_load_job_raises_for_failed_url(monkeypatch):
    def fake_get(url: str, **_) -> httpx.Response:
        return httpx.Response(403, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(httpx.HTTPStatusError):
        load_job("https://jobs.example.com/123")
