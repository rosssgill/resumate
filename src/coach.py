from html.parser import HTMLParser
from pathlib import Path

import httpx
import pydantic_ai
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model

from models import Resume

# The first-run promotional banner would interleave with the CLI's own output.
# The library types this flag as Literal[True] although disabling it is documented.
pydantic_ai.BANNER_ENABLED = False  # ty: ignore[invalid-assignment]

INSTRUCTIONS = """\
You are an experienced technical recruiter and resume coach. Review the resume, \
given in JSON Resume format, and give specific, actionable feedback.

- Focus on what most improves the resume: vague or duty-based bullets, missing \
impact or numbers, weak or repeated verbs, inconsistent tense, wordiness, typos, \
and anything that makes it harder to skim.
- Point each suggestion at the field it concerns using dot notation with \
zero-based indices, e.g. work.0.highlights.2 or basics.summary. Use "general" \
for resume-wide points.
- Only raise issues you can see in the resume text, and quote the exact original \
text each suggestion is about.
- Rewrites may only rephrase, reorder, merge or cut what the resume already says. \
Every specific in a rewrite (number, technology, method, scope, purpose or \
outcome) must already appear in the resume. Anything else, including a number \
that would help, must be a [placeholder] for the candidate to fill in or delete.
- Don't add unsupported claims such as "at scale", "proven track record" or \
"deep expertise". Write in the resume's voice, never in the first person.
- Keep the resume's **bold** markup convention in rewrites.
- If a job posting is given, prioritise relevance to it and name gaps, but never \
suggest claiming experience the resume doesn't support.
- Order suggestions by impact, most important first, and give at most 12.
"""


class Suggestion(BaseModel):
    path: str = Field(description="Field the suggestion is about, or 'general'")
    original: str | None = Field(
        default=None, description="Exact text from the resume this is about"
    )
    issue: str = Field(description="What is weak and why, in one or two sentences")
    rewrite: str | None = Field(
        default=None, description="Suggested replacement text, if applicable"
    )


class Feedback(BaseModel):
    summary: str = Field(description="Two or three sentence overall assessment")
    suggestions: list[Suggestion]


coach_agent: Agent[None, Feedback] = Agent(
    output_type=Feedback, instructions=INSTRUCTIONS
)


class _TextExtractor(HTMLParser):
    """Collects visible text, skipping scripts and styles."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and data.strip():
            self.parts.append(data.strip())


def load_job(source: str) -> str:
    """Read a job posting from a file path or an http(s) URL."""
    if not source.startswith(("http://", "https://")):
        return Path(source).read_text(encoding="utf-8")
    response = httpx.get(source, follow_redirects=True, timeout=30)
    response.raise_for_status()
    extractor = _TextExtractor()
    extractor.feed(response.text)
    return "\n".join(extractor.parts)


def coach(resume: Resume, *, model: Model | str, job: str | None = None) -> Feedback:
    prompt = "Resume:\n" + resume.model_dump_json(
        by_alias=True, exclude_defaults=True, indent=2
    )
    if job:
        prompt += f"\n\nJob posting to tailor the feedback to:\n{job}"
    return coach_agent.run_sync(prompt, model=model).output
