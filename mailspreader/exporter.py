import csv
import json
from typing import List, Tuple, Dict, Union
import os

def save_list_to_csv(filepath: str, data: List[str]) -> None:
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for item in data:
            writer.writerow([item])

def load_list_from_csv(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row[0] for row in reader if row]

def save_dicts_to_csv(filepath: str, headers: List[str], rows: List[Dict[str, str]]) -> None:
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def load_dicts_from_csv(filepath: str) -> List[Dict[str, str]]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_metadata(filepath: str, names: List[str], websites: List[str], abouts: List[str]) -> None:
    rows = [{"name": n, "website": w, "about": a} for n, w, a in zip(names, websites, abouts)]
    save_dicts_to_csv(filepath, ["name", "website", "about"], rows)

def load_metadata(filepath: str) -> Tuple[List[str], List[str], List[str]]:
    rows = load_dicts_from_csv(filepath)
    return (
        [r["name"] for r in rows],
        [r["website"] for r in rows],
        [r["about"] for r in rows],
    )

def save_input_params(filepath: str, params: Dict) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(params, f, ensure_ascii=False, indent=2)

def load_input_params(filepath: str) -> Dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def export_to_spreadsheet(names: List[str], summaries: List[str], emails: List[str], folder="data", filename="prospect_list.csv"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Company Name", "Business Summary", "Email"])
        for name, summary, email in zip(names, summaries, emails):
            writer.writerow([name, summary, email])
