import typer
from pathlib import Path

app = typer.Typer(help="Mail Spreader - utilities to automate LinkedIn-based mailings",pretty_exceptions_enable=False)

@app.command()
def list_industries_to_linkedin_url(
    yaml_file_industries: Path = typer.Argument(..., help="YAML industries file"),
    yaml_file_url: Path = typer.Option(..., "--output", "-o", help="YAML url file")
):
    """Convert a list of industries into a LinkedIn URL"""
    from .scraper import linkedin_url_creator as creator

    creator(yaml_file_industries, yaml_file_url)

@app.command()
def linkedin_url_to_profil_json(
    yaml_file: Path = typer.Argument(..., help="YAML config file"),
    json_file: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use LinkedinIn url to make a JSON of entreprise profile URLs"""
    from .scraper import scrape_linkedin_company_profiles as scrap

    scrap(yaml_file, json_file)

@app.command()
def profil_url_to_metadata_json(
    yaml_file: Path = typer.Argument(..., help="YAML config file"),
    json_file_profil: Path = typer.Argument(..., help="Input JSON file"),
    json_file_metadata: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use Entreprise profile URLs to make a JSON of their metadata"""
    from .scraper import extract_company_metadata as extract

    extract(yaml_file, json_file_profil, json_file_metadata="metadata.json")

@app.command()
def metadata_json_to_email_json(
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_email: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use metadata json to make a JSON of email"""
    from .parser import extract_contact_emails as parser

    parser(json_file_metadata, json_file_email)

@app.command()
def metadata_json_to_summaries_json(
    yaml_file: Path = typer.Argument(..., help="YAML config file"),
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_email: Path = typer.Argument(..., help="Input JSON file"),
    json_file_summaries: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use metadata json to make a JSON of summaries"""
    from .summarizer import generate_summaries_extra as summarizer

    summarizer(yaml_file, json_file_email, json_file_metadata, json_file_summaries)

@app.command()
def metadata_email_json_to_spreadsheet(
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_email: Path = typer.Argument(..., help="Input JSON file"),
    json_file_summaries: Path = typer.Argument(..., help="Input JSON file"),
    csv_file: Path = typer.Option(..., "--output", "-o", help="Output CSV file")
):
    """Use metadata json to make a JSON of email"""
    from .export import export_to_spreadsheet as export

    export(json_file_metadata, json_file_email, json_file_summaries, csv_file)

if __name__ == "__main__":
    app()
