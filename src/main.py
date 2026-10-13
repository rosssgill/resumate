from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from models import Resume
from render import render_pdf

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
) -> None:
    """
    Compile a resume from a JSON Resume file into a PDF.
    """
    try:
        resume = Resume.model_validate_json(file_path.read_text())
    except ValidationError as error:
        typer.echo(f"Invalid resume in {file_path}:\n{error}", err=True)
        raise typer.Exit(1) from error

    output_path = output or file_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(render_pdf(resume))
    typer.echo(f"Wrote {output_path}")


if __name__ == "__main__":
    app()
