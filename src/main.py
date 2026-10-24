from pathlib import Path
from typing import Annotated, Any

import httpx
import typer
from pydantic import ValidationError
from pydantic_ai.exceptions import AgentRunError, UserError

from coach import Feedback, Suggestion, coach, load_job
from core.config import Paper, Settings, load_env_file
from models import Resume
from render import render_to_fit

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "A declarative Python based CLI tool that generates resumes from "
        "JSON Resume files using Typst templates"
    ),
)


@app.callback()
def main() -> None:
    load_env_file()


ResumePath = Annotated[
    Path,
    typer.Argument(help="Path to the JSON Resume file", exists=True, dir_okay=False),
]


def load_settings(**overrides: Any) -> Settings:
    """Settings from the environment, overridden by any CLI flags that were passed."""
    try:
        return Settings(**{k: v for k, v in overrides.items() if v is not None})
    except ValidationError as error:
        typer.echo(f"Invalid settings:\n{error}", err=True)
        raise typer.Exit(1) from error


def load_resume(file_path: Path) -> Resume:
    try:
        return Resume.model_validate_json(file_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as error:
        typer.echo(f"{file_path} is not valid UTF-8: {error}", err=True)
        raise typer.Exit(1) from error
    except ValidationError as error:
        typer.echo(f"Invalid resume in {file_path}:\n{error}", err=True)
        raise typer.Exit(1) from error


@app.command()
def compile(
    file_path: ResumePath,
    output: Annotated[
        Path | None,
        typer.Option(
            help="Where to write the PDF", show_default="input path with .pdf"
        ),
    ] = None,
    max_pages: Annotated[
        int | None,
        typer.Option(
            min=1,
            help="Shrink the text to fit within this many pages",
            show_default="1, or RESUMATE_MAX_PAGES",
        ),
    ] = None,
    paper: Annotated[
        Paper | None,
        typer.Option(help="Paper size", show_default="a4, or RESUMATE_PAPER"),
    ] = None,
) -> None:
    """
    Compile a resume from a JSON Resume file into a PDF.
    """
    settings = load_settings(max_pages=max_pages, paper=paper)
    resume = load_resume(file_path)
    output_path = output or file_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_to_fit(resume, settings)
    output_path.write_bytes(rendered.pdf)
    pages = f"{rendered.pages} page{'s' if rendered.pages > 1 else ''}"
    typer.echo(f"Wrote {output_path} ({pages}, {rendered.font_size:g}pt text)")
    if rendered.pages > settings.max_pages:
        typer.echo(
            f"Warning: resume exceeds the {settings.max_pages} page limit "
            "even at the smallest text size",
            err=True,
        )


def print_feedback(feedback: Feedback) -> None:
    typer.secho("Summary", bold=True)
    typer.echo(f"{feedback.summary}\n")
    # Group by section, keeping the model's most-impactful-first order within each
    sections: dict[str, list[Suggestion]] = {}
    for suggestion in feedback.suggestions:
        sections.setdefault(suggestion.path.split(".")[0], []).append(suggestion)
    for section, suggestions in sections.items():
        typer.secho(section.capitalize(), bold=True)
        for suggestion in suggestions:
            typer.secho(f"  {suggestion.path}", fg=typer.colors.CYAN)
            typer.echo(f"    {suggestion.issue}")
            if suggestion.original and suggestion.rewrite:
                typer.secho(f"    - {suggestion.original}", fg=typer.colors.RED)
            if suggestion.rewrite:
                typer.secho(f"    + {suggestion.rewrite}", fg=typer.colors.GREEN)
        typer.echo()


@app.command("coach")
def coach_command(
    file_path: ResumePath,
    model: Annotated[
        str | None,
        typer.Option(
            help="Model to use, e.g. anthropic:claude-sonnet-5-5 or ollama:qwen3",
            show_default="RESUMATE_MODEL",
        ),
    ] = None,
    job: Annotated[
        str | None,
        typer.Option(help="Job posting to tailor feedback to, as a file path or URL"),
    ] = None,
) -> None:
    """
    Get feedback and suggested rewrites for a resume from an LLM of your choice.
    """
    model = load_settings(model=model).model
    if not model:
        typer.echo(
            "No model chosen. Pass --model or set RESUMATE_MODEL in your "
            "environment or a .env file, "
            "e.g. anthropic:claude-sonnet-5-5 or ollama:qwen3.",
            err=True,
        )
        raise typer.Exit(1)
    resume = load_resume(file_path)
    try:
        job_text = load_job(job) if job else None
    except (OSError, httpx.HTTPError) as error:
        typer.echo(f"Could not read job posting {job}: {error}", err=True)
        raise typer.Exit(1) from error
    try:
        feedback = coach(resume, model=model, job=job_text)
    except (UserError, AgentRunError) as error:
        typer.echo(f"Coaching failed: {error}", err=True)
        raise typer.Exit(1) from error
    print_feedback(feedback)


if __name__ == "__main__":
    app()
