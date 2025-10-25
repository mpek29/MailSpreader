import os
import json
import csv

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
