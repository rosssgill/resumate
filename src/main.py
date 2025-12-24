import typer

app = typer.Typer()

@app.command()
def compile(
    file_path: str = typer.Argument(..., help="Path to the YAML file containing resume data"),
    output_type: str = typer.Option("pdf", help="Output format (e.g., pdf, docx)")
):
    """
    Compile a resume from a YAML file into a PDF using LaTeX templates.
    """
    typer.echo(f"Compiling resume from {file_path} into {output_type} format...")


if __name__ == "__main__":
    app()
