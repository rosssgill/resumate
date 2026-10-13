from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from models import Resume
from render import Paper, render_to_fit

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "A declarative Python based CLI tool that generates resumes from "
        "JSON Resume files using Typst templates"
    ),
)


@app.command()
def compile(
    file_path: Annotated[
        Path,
        typer.Argument(
            help="Path to the JSON Resume file", exists=True, dir_okay=False
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            help="Where to write the PDF", show_default="input path with .pdf"
        ),
    ] = None,
    max_pages: Annotated[
        int, typer.Option(min=1, help="Shrink the text to fit within this many pages")
    ] = 1,
    paper: Annotated[Paper, typer.Option(help="Paper size")] = Paper.A4,
) -> None:
    """
    Compile a resume from a JSON Resume file into a PDF.
    """
    try:
        resume = Resume.model_validate_json(file_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as error:
        typer.echo(f"{file_path} is not valid UTF-8: {error}", err=True)
        raise typer.Exit(1) from error
    except ValidationError as error:
        typer.echo(f"Invalid resume in {file_path}:\n{error}", err=True)
        raise typer.Exit(1) from error

    output_path = output or file_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_to_fit(resume, max_pages=max_pages, paper=paper)
    output_path.write_bytes(rendered.pdf)
    pages = f"{rendered.pages} page{'s' if rendered.pages > 1 else ''}"
    typer.echo(f"Wrote {output_path} ({pages}, {rendered.font_size:g}pt text)")
    if rendered.pages > max_pages:
        typer.echo(
            f"Warning: resume exceeds the {max_pages} page limit "
            "even at the smallest text size",
            err=True,
        )


if __name__ == "__main__":
    app()
