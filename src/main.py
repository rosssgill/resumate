import typer

from enum import Enum
from typing import Generator
from typing_extensions import Annotated


class OutputType(str, Enum):
    PDF = "PDF"
    LATEX = "LaTeX"


VALID_OUTPUT_TYPES = [output_type.value for output_type in OutputType]


def complete_output_type(incomplete: str) -> Generator[str, None, None]:
    for output_type in VALID_OUTPUT_TYPES:
        if output_type.startswith(incomplete.upper()):
            yield output_type


app = typer.Typer(
    no_args_is_help=True,
    help="A declarative Python based CLI tool that generates resumes from YAML files using LaTeX templates",
)


@app.command()
def compile(
    file_path: Annotated[
        str, typer.Argument(help="Path to the YAML file containing resume data")
    ],
    output_type: Annotated[
        str, typer.Option(help="Output format", autocompletion=complete_output_type)
    ] = OutputType.PDF.value,
) -> None:
    """
    Compile a resume from a YAML file into a PDF using LaTeX templates.
    """
    typer.echo(f"Compiling resume from {file_path} into {output_type} format...")


if __name__ == "__main__":
    app()
