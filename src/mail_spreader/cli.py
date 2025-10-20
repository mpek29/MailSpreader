import re
import typer
import json
from pathlib import Path
import yaml
from typing import List
import csv
from urllib.parse import urlparse


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

    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    base_search_url = config.get("base_search_url", [])
    if not isinstance(base_search_url, list):
        base_search_url = [base_search_url]
    linkedin_email = config.get("linkedin_email", "")
    linkedin_password = config.get("linkedin_password", "")

    collected_profile_urls = []
    for url in base_search_url:
        collected_profile_urls.extend(scrap(url, linkedin_email, linkedin_password))

    data = {
        "collected_profile_urls": collected_profile_urls
    }

    # Sauvegarder en JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.command()
def profil_url_to_metadata_json(
    yaml_file: Path = typer.Argument(..., help="YAML config file"),
    json_file_profil: Path = typer.Argument(..., help="Input JSON file"),
    json_file_metadata: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use Entreprise profile URLs to make a JSON of their metadata"""
    from .scraper import extract_company_metadata as extract

    extract(yaml_file, json_file_profil, json_file_metadata="metadata.json")



# --- colle ton tableau brut ici (ou charge depuis un fichier) ---
RAW_PROXY_TABLE = """
185.162.230.83	80	Armenia	3880 ms	HTTP	no	1 minutes
188.114.96.240	80		3300 ms	HTTP	no	1 minutes
172.65.90.0	80		1300 ms	HTTP	no	1 minutes
172.64.33.160	80		2360 ms	HTTP	no	1 minutes
141.101.121.160	80		80 ms	HTTP	no	1 minutes
141.101.90.99	80	United States	200 ms	HTTP	no	1 minutes
5.129.232.77	1080	Netherlands Amsterdam	3560 ms	SOCKS5	High	1 minutes
192.252.209.158	4145	United States	1060 ms	SOCKS4	High	1 minutes
164.38.155.87	80	United Kingdom	4960 ms	HTTP	no	2 minutes
195.85.23.106	80	Czech Republic	3480 ms	HTTP	no	2 minutes
185.162.231.38	80	Armenia	3560 ms	HTTP	no	2 minutes
172.64.152.203	80	United States	2660 ms	HTTP	no	2 minutes
185.162.231.111	80	Armenia	2860 ms	HTTP	no	2 minutes
40.177.65.8	80	Canada Calgary	580 ms	HTTP	Average	2 minutes
172.67.79.59	80	United States	2180 ms	HTTP	no	2 minutes
172.64.149.158	80	United States	2060 ms	HTTP	no	2 minutes
46.245.123.10	8080	Iran	5100 ms	HTTP	no	2 minutes
34.194.41.221	80	United States Ashburn	540 ms	HTTP	Average	2 minutes
172.67.71.152	80	United States	100 ms	HTTP	no	2 minutes
141.101.123.86	80		100 ms	HTTP	no	2 minutes
172.67.70.178	80	United States	100 ms	HTTP	no	2 minutes
47.206.214.2	54321	United States Bradenton	800 ms	SOCKS4	High	2 minutes
37.32.24.181	1080	Iran	5100 ms	SOCKS5	High	2 minutes
202.5.48.84	1080	Bangladesh	1560 ms	SOCKS5	High	2 minutes
72.195.34.35	27360	United States	920 ms	SOCKS4	High	2 minutes
98.191.0.47	4145	United States Tempe	880 ms	SOCKS4	High	2 minutes
192.252.209.155	14455	Canada Toronto	1020 ms	SOCKS4	High	2 minutes
185.112.151.207	8022	Iran	4320 ms	HTTP	no	2 minutes
185.88.177.197	8081	Iran	700 ms	HTTP	High	2 minutes
103.118.46.176	8080	Cambodia Phnom Penh	860 ms	HTTP	High	4 minutes
172.64.68.47	80	United States	2360 ms	HTTP	no	4 minutes
141.101.122.26	80		80 ms	HTTP	no	4 minutes
23.227.39.19	80	Canada	20 ms	HTTP	no	4 minutes
185.88.177.197	80	Iran	820 ms	HTTP	High	4 minutes
128.140.113.110	8080	Germany Falkenstein	220 ms	HTTP	High	5 minutes
84.242.58.9	8080	Palestinian Territory	5100 ms	HTTP	no	5 minutes
202.5.62.55	8080	Bangladesh	3180 ms	HTTP	no	5 minutes
45.162.225.114	59341	Brazil Olinda	1140 ms	SOCKS4	High	5 minutes
206.220.175.2	4145	United States	1800 ms	SOCKS4	High	5 minutes
68.71.247.130	4145		1140 ms	SOCKS4	High	5 minutes
199.116.114.11	4145	United States	1140 ms	SOCKS4	High	5 minutes
72.207.33.64	4145	United States Chula Vista	900 ms	SOCKS4	High	5 minutes
72.223.188.92	4145	United States Mesa	880 ms	SOCKS4	High	5 minutes
208.102.51.6	58208	United States Alexandria	4540 ms	SOCKS4	High	6 minutes
185.162.229.56	80	Armenia	2060 ms	HTTP	no	6 minutes
69.84.182.21	80	United States	20 ms	HTTP	no	6 minutes
185.238.228.128	80	Spain	760 ms	HTTP	no	6 minutes
141.101.120.216	80		100 ms	HTTP	no	6 minutes
198.177.254.131	4145	United States	2840 ms	SOCKS4	High	6 minutes
192.252.220.92	17328	United States Los Angeles	1140 ms	SOCKS4	High	6 minutes
72.207.113.97	4145	United States San Diego	880 ms	SOCKS4	High	6 minutes
68.71.252.38	4145	United States	2160 ms	SOCKS4	High	7 minutes
199.58.184.97	4145	United States	1060 ms	SOCKS4	High	7 minutes
192.252.215.5	16137	Canada Toronto	1060 ms	SOCKS4	High	7 minutes
192.252.211.193	4145	United States	1060 ms	SOCKS4	High	7 minutes
198.8.94.170	4145	United States	1040 ms	SOCKS4	High	7 minutes
72.206.74.126	4145	United States Fairfax	880 ms	SOCKS4	High	7 minutes
192.111.137.37	18762	United States	1040 ms	SOCKS4	High	7 minutes
200.43.231.17	4145	Argentina Oberá	1440 ms	SOCKS4	High	7 minutes
152.53.107.230	80	Netherlands Amsterdam	200 ms	HTTP	High	7 minutes
223.25.100.236	8080	Indonesia	4160 ms	HTTP	no	7 minutes
202.5.60.46	1080	Bangladesh	4140 ms	SOCKS5	High	7 minutes
62.84.96.215	1080	Netherlands	1420 ms	SOCKS5	High	7 minutes
115.127.132.225	1080	Bangladesh Gazipur	4300 ms	SOCKS5	High	7 minutes
"""


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
def metadata_json_to_summaries_json(
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_summaries: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use metadata JSON to make a JSON of summaries"""
    from .summarizer import generate_summaries_extra as summarizer

    summarizer(json_file_metadata, json_file_summaries)

@app.command()
def summaries_json_en_to_fr(
    json_file_en: Path = typer.Argument(..., help="Input JSON file"),
    json_file_fr: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """Use summaries JSON to make a JSON of summaries in french"""
    from .summarizer import translate_json as trans

    trans(json_file_en, json_file_fr)

@app.command()
def metadata_email_json_to_spreadsheet(
    json_file_metadata: Path = typer.Argument(..., help="Input JSON file"),
    json_file_email: Path = typer.Argument(..., help="Input JSON file"),
    json_file_summaries: Path = typer.Argument(..., help="Input JSON file"),
    csv_file: Path = typer.Option(..., "--output", "-o", help="Output CSV file")
):
    """Use a lot of JSON to make a spreadsheet of all the different data"""
    from .export import export_to_spreadsheet as export

    export(json_file_metadata, json_file_email, json_file_summaries, csv_file)

@app.command()
def split_urls(
    json_file: Path = typer.Argument(..., help="Fichier JSON d'entrée avec clé 'collected_profile_urls'"),
    output_dir: Path = typer.Argument(..., help="Dossier où créer les fichiers de sortie"),
    chunk_size: int = typer.Option(50, "--chunk-size", "-c", help="Taille des paquets")
):
    """
    Découpe un JSON contenant {"collected_profile_urls": [...]} en plusieurs fichiers JSON,
    chacun contenant un paquet d'URLs, et les range dans un sous-dossier.
    """

    # Lire le fichier d'entrée
    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "collected_profile_urls" not in data or not isinstance(data["collected_profile_urls"], list):
        typer.echo("Erreur: le JSON doit contenir une clé 'collected_profile_urls' avec une liste d'URLs.")
        raise typer.Exit(code=1)

    urls = data["collected_profile_urls"]

    # Créer le dossier de sortie
    output_subdir = output_dir / json_file.stem
    output_subdir.mkdir(parents=True, exist_ok=True)

    # Découpage en paquets
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        chunk_file = output_subdir / f"chunk_{i // chunk_size + 1}.json"
        with chunk_file.open("w", encoding="utf-8") as f:
            json.dump({"collected_profile_urls": chunk}, f, ensure_ascii=False, indent=2)

    typer.echo(f"Création terminée. Les fichiers sont dans {output_subdir}")

def merge_json_files(json_files: List[Path]) -> dict:
    merged_data = {
        "company_names": [],
        "company_websites": [],
        "company_about_texts": []
    }

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged_data["company_names"].extend(data.get("company_names", []))
            merged_data["company_websites"].extend(data.get("company_websites", []))
            merged_data["company_about_texts"].extend(data.get("company_about_texts", []))
    
    return merged_data

@app.command()
def merge_json_folder_to_json(
    folder: Path = typer.Argument(..., help="Folder containing JSON files"),
    output_file: Path = typer.Option(..., "--output", "-o", help="Output JSON file")
):
    """
    Merge all JSON files in a folder into a single JSON file
    """
    json_files = list(folder.glob("*.json"))
    if not json_files:
        typer.echo("No JSON files found in the folder.")
        raise typer.Exit(code=1)

    merged_json = merge_json_files(json_files)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_json, f, ensure_ascii=False, indent=2)

    typer.echo(f"Merged JSON saved to {output_file}")

def clean_json_file(input_file: Path) -> Path:
    """
    Clean a JSON file by removing entries with empty 'company_websites' or 'company_about_texts'.
    Returns the path to the cleaned JSON file.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Créer de nouvelles listes filtrées
    cleaned_names = []
    cleaned_websites = []
    cleaned_about_texts = []

    for name, website, about in zip(
        data.get("company_names", []),
        data.get("company_websites", []),
        data.get("company_about_texts", [])
    ):
        if website.strip() and about.strip():  # supprime les entrées vides
            cleaned_names.append(name)
            cleaned_websites.append(website)
            cleaned_about_texts.append(about)

    cleaned_data = {
        "company_names": cleaned_names,
        "company_websites": cleaned_websites,
        "company_about_texts": cleaned_about_texts
    }

    # Générer le nom du fichier de sortie
    output_file = input_file.with_name(f"{input_file.stem}_cleaned.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    return output_file

@app.command()
def clean_json(
    input_file: Path = typer.Argument(..., help="Input JSON file to clean")
):
    cleaned_file = clean_json_file(input_file)
    typer.echo(f"Cleaned JSON saved to {cleaned_file}")

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

def extract_number(filename: str) -> list[int]:
    """
    Extrait toutes les séquences de chiffres d'un nom de fichier
    afin de pouvoir trier de manière numérique.
    Exemple :
        "email_3_1.json" -> [3, 1]
        "email_10.json"  -> [10]
    """
    return [int(num) for num in re.findall(r"\d+", filename)]


@app.command()
def merge_email_json_folder(
    input_folder: Path = typer.Argument(..., help="Folder containing JSON files"),
    output_file: Path = typer.Argument(..., help="Output merged JSON file"),
):
    """
    Merge all JSON files from a folder into a single JSON file.
    Assumes each JSON has the structure {"extracted_emails": [..]}.
    Sorting is done by numeric order of filenames.
    """
    merged_data = {"extracted_emails": []}

    # Récupération + tri numérique des fichiers (tous les .json, insensible à la casse)
    files = sorted(
        [f for f in input_folder.iterdir() if f.suffix.lower() == ".json"],
        key=lambda f: extract_number(f.name)
    )

    for json_file in files:
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if "extracted_emails" in data and isinstance(data["extracted_emails"], list):
                    print(f"{json_file.name}: {len(data['extracted_emails'])} emails")  # diagnostic
                    merged_data["extracted_emails"].extend(data["extracted_emails"])
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON file: {json_file}")

    # Conserver tous les emails tels quels, y compris vides et doublons
    merged_data["extracted_emails"] = [email.strip() for email in merged_data["extracted_emails"]]

    # Écriture du JSON fusionné
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    typer.echo(f"Merged JSON saved to {output_file}")

def extraire_domaine(email: str) -> str:
    return email.split('@')[-1].lower()

def extraire_domaine_site(site_url: str) -> str:
    netloc = urlparse(site_url).netloc.lower()
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    return netloc

@app.command()
def emails_to_csv(
    websites_json: Path = typer.Argument(..., help="JSON file containing company websites"),
    emails_json: Path = typer.Argument(..., help="JSON file containing extracted emails"),
    csv_file: Path = typer.Option(..., "--output", "-o", help="Output CSV file")
):
    """
    Associe les emails aux sites web et produit un CSV (website,email)
    """
    # Charger les emails
    with open(emails_json, 'r', encoding='utf-8') as f:
        emails_data = json.load(f)
    emails = emails_data.get("extracted_emails", [])

    # Charger les sites
    with open(websites_json, 'r', encoding='utf-8') as f:
        sites_data = json.load(f)
    sites = sites_data.get("company_websites", [])

    # Construire dictionnaire domaine -> email
    email_domain_map = {extraire_domaine(email): email for email in emails}

    # Associer site -> email
    site_email_map = {}
    for site in sites:
        site_domain = extraire_domaine_site(site)
        matched_email = next(
            (email for domain, email in email_domain_map.items() if domain in site_domain or site_domain in domain),
            None
        )
        site_email_map[site] = matched_email

    # Écrire CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['website', 'email'])
        for site, email in site_email_map.items():
            writer.writerow([site, email or ""])

    typer.echo(f"CSV généré : {csv_file}")

if __name__ == "__main__":
    app()