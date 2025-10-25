import os
import json
import csv
from pathlib import Path

def export_to_spreadsheet(json_file_metadata, json_file_email, json_file_summaries, csv_file):
    dir_path = os.path.dirname(csv_file)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(json_file_metadata, "r", encoding="utf-8") as f:
        metadata_json = json.load(f)

    names = metadata_json.get("company_names", [])
    websites = metadata_json.get("company_websites", [])

    with open(json_file_summaries, "r", encoding="utf-8") as f:
        summaries_json = json.load(f)

    summaries = summaries_json.get("summaries", [])

    with open(json_file_email, "r", encoding="utf-8") as f:
        email_json = json.load(f)

    emails = email_json.get("extracted_emails", [])

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Business Summary", "Email", "Website"])
        for name, summary, email, website in zip(names, summaries, emails, websites):
            writer.writerow([name, summary, email, website])

def export_to_spreadsheet_without_summaries(json_file_metadata, json_file_email, csv_file):
    dir_path = os.path.dirname(csv_file)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(json_file_metadata, "r", encoding="utf-8") as f:
        metadata_json = json.load(f)

    names = metadata_json.get("company_names", [])
    websites = metadata_json.get("company_websites", [])

    with open(json_file_email, "r", encoding="utf-8") as f:
        email_json = json.load(f)

    emails = email_json.get("extracted_emails", [])

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Email", "Website"])
        for name, email, website in zip(names, emails, websites):
            writer.writerow([name, email, website])

def filter_spreadsheet_interactively(input_csv: Path, output_csv: Path):
    """
    Lit un fichier CSV contenant les colonnes : Company Name, Email, Website.
    Pour chaque ligne, demande à l'utilisateur s'il veut la conserver.
    Écrit un nouveau CSV avec uniquement les lignes conservées.
    """
    dir_path = os.path.dirname(output_csv)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    filtered_rows = []

    with open(input_csv, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError("Le fichier CSV d'entrée ne contient pas d'en-têtes valides.")

        for row in reader:
            name = row.get("Company Name", "")
            email = row.get("Email", "")
            website = row.get("Website", "")
            print(f"\nEntreprise : {name}\nEmail : {email}\nSite web : {website}")
            choice = input("Conserver cette ligne ? (o/n) : ").strip().lower()
            if choice == "o":
                filtered_rows.append(row)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

    print(f"\nNouveau fichier généré : {output_csv}")
