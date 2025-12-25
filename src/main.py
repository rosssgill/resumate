import typer

from typing_extensions import Annotated

app = typer.Typer(no_args_is_help=True, help="A declarative Python based CLI tool that generates resumes from YAML files using LaTeX templates")

@app.command()
def compile(
    file_path: Annotated[str, typer.Argument(help="Path to the YAML file containing resume data")],
    output_type: Annotated[str, typer.Option(help="Output format")] = "pdf",
):
    """
    Compile a resume from a YAML file into a PDF using LaTeX templates.
    """
    typer.echo(f"Compiling resume from {file_path} into {output_type} format...")

if __name__ == "__main__":
    app()
