import os
import json
import csv

def export_to_spreadsheet(json_file_metadata, json_file_email, json_file_summaries, csv_file):
    dir_path = os.path.dirname(csv_file)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(json_file_metadata, "r", encoding="utf-8") as f:
        metadata_json = json.load(f)

    # Récupérer la liste des URLs
    names = metadata_json.get("company_names", [])

    with open(json_file_summaries, "r", encoding="utf-8") as f:
        summaries_json = json.load(f)

    # Récupérer la liste des URLs
    summaries = summaries_json.get("summaries", [])

    with open(json_file_email, "r", encoding="utf-8") as f:
        email_json = json.load(f)

    # Récupérer la liste des URLs
    emails = email_json.get("extracted_emails", [])

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Business Summary", "Email"])
        for name, summary, email in zip(names, summaries, emails):
            writer.writerow([name, summary, email])