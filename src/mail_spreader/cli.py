import typer
from pathlib import Path

app = typer.Typer(help="Mail Spreader - utilities to automate LinkedIn-based mailings",pretty_exceptions_enable=False)


@app.command()
def list_industries_to_linkedin_url(
    yaml_file_industries: Path = typer.Argument(..., help="YAML industries file"),
    yaml_file_url: Path = typer.Option(None, "--output", "-o", help="YAML url file")
):
    """Convert a list of industries into a LinkedIn URL"""
    from .scraper  import linkedin_url_creator  as creator
    
    creator(yaml_file_industries, yaml_file_url)

@app.command()
def list_industries_to_linkedin_list_urls(
    yaml_file_industries: Path = typer.Argument(..., help="YAML industries file"),
    yaml_file_url: Path = typer.Option(..., "--output", "-o", help="YAML url file")
):
    """Convert a list of industries into a list of LinkedIn URL"""
    from .scraper import linkedin_list_urls_creator as creator

    creator(yaml_file_industries, yaml_file_url)

if __name__ == "__main__":
    app()