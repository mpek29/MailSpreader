import typer
from pathlib import Path
import json

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

    extract(yaml_file, json_file_profil, json_file_metadata)

@app.command()
def metadata_json_to_email_json_auto(
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_email: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use metadata JSON to make automatically a JSON of email"""
    from .parser import extract_contact_emails_auto
    from .utils import parse_proxy_table, DEFAULT_USER_AGENT_POOL

    # parse and filter proxies from the RAW table (threshold_ms adjustable)
    user_agent_pool = DEFAULT_USER_AGENT_POOL  # ou personnaliser/étendre

    # internal defaults (pas de changement CLI)
    extract_contact_emails_auto(
        json_file_metadata,
        json_file_email,
        user_agent_pool=user_agent_pool,
        requests_per_minute=20,
        min_delay=3,
        max_delay=9,
        max_driver_pool_size=6,
        headless=False
    )

@app.command()
def metadata_json_to_email_json_manual(
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_email: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use metadata JSON to make with the help of an operator a JSON of email"""
    from .parser import extract_contact_emails_manual as parser

    parser(json_file_metadata, json_file_email)

@app.command()
def split_companies(
    json_file: Path = typer.Argument(..., help="Fichier JSON d'entrée"),
    output_dir: Path = typer.Argument(..., help="Dossier où créer les fichiers de sortie"),
    chunk_size: int = typer.Option(50, "--chunk-size", "-c", help="Taille des paquets")
):
    """
    Découpe un JSON contenant { company_names, company_websites, company_about_texts }
    en plusieurs fichiers JSON synchronisés.
    """

    # Lire le fichier d'entrée
    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Vérification des clés attendues
    expected_keys = ["company_names", "company_websites", "company_about_texts"]
    for key in expected_keys:
        if key not in data or not isinstance(data[key], list):
            typer.echo(f"Erreur: le JSON doit contenir une clé '{key}' avec une liste.")
            raise typer.Exit(code=1)

    names = data["company_names"]
    websites = data["company_websites"]
    abouts = data["company_about_texts"]

    # Vérification que les listes ont la même longueur
    if not (len(names) == len(websites) == len(abouts)):
        typer.echo("Erreur: Les listes n'ont pas toutes la même longueur.")
        raise typer.Exit(code=1)

    # Créer le dossier de sortie
    output_subdir = output_dir / json_file.stem
    output_subdir.mkdir(parents=True, exist_ok=True)

    # Découpage en paquets synchronisés
    for i in range(0, len(names), chunk_size):
        chunk_names = names[i:i + chunk_size]
        chunk_websites = websites[i:i + chunk_size]
        chunk_abouts = abouts[i:i + chunk_size]

        chunk_data = {
            "company_names": chunk_names,
            "company_websites": chunk_websites,
            "company_about_texts": chunk_abouts
        }

        chunk_file = output_subdir / f"chunk_{i // chunk_size + 1}.json"
        with chunk_file.open("w", encoding="utf-8") as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)

    typer.echo(f"Création terminée. Les fichiers sont dans {output_subdir}")


@app.command()
def merge_email_jsons(
    input_folder: str = typer.Argument(..., help="Dossier contenant les fichiers JSON à fusionner."),
    output_file: str = typer.Option("merged_emails.json", "--output", "-o", help="Nom du fichier JSON de sortie.")
):
    """
    Fusionne tous les fichiers JSON du dossier spécifié en un seul.
    """
    from .parser import merge_extracted_email_jsons as merge

    if not os.path.isdir(input_folder):
        typer.echo(f"❌ Le dossier spécifié n'existe pas: {input_folder}")
        raise typer.Exit(code=1)

    result = merge(input_folder, output_file)
    typer.echo(f"✅ Fusion terminée : {len(result['extracted_emails'])} emails sauvegardés dans {result['output_file']}.")

if __name__ == "__main__":
    app()
