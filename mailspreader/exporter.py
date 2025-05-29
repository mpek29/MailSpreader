import csv
import os

def export_to_spreadsheet(names, summaries, emails, folder="data", filename="prospect_list.csv"):
    os.makedirs(folder, exist_ok=True)  # Create folder if not exists
    path = os.path.join(folder, filename)

    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["Company Name", "Business Summary", "Email"])
        # Write rows
        for name, summary, email in zip(names, summaries, emails):
            writer.writerow([name, summary, email])
