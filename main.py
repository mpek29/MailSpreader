import os
from typing import List, Tuple

from mailspreader.linkedin_scraper import (
    scrape_linkedin_company_profiles,
    extract_company_metadata,
)
from mailspreader.website_parser import extract_contact_emails
from mailspreader.summarizer import generate_summaries
from mailspreader.exporter import (
    save_list_to_csv,
    load_list_from_csv,
    save_metadata,
    load_metadata,
    save_input_params,
    load_input_params,
    export_to_spreadsheet,
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

PROFILE_URLS_CSV = os.path.join(DATA_DIR, "step1_profile_urls.csv")
METADATA_CSV = os.path.join(DATA_DIR, "step2_metadata.csv")
EMAILS_CSV = os.path.join(DATA_DIR, "step3_emails.csv")
SUMMARIES_CSV = os.path.join(DATA_DIR, "step4_summaries.csv")
INPUT_PARAMS_JSON = os.path.join(DATA_DIR, "input_params.json")


def main() -> None:
    steps = {
        1: "Scrape company profile URLs",
        2: "Extract company metadata",
        3: "Extract contact emails",
        4: "Generate summaries",
        5: "Export to spreadsheet",
    }

    existing_steps = []
    if os.path.exists(PROFILE_URLS_CSV):
        existing_steps.append(1)
    if os.path.exists(METADATA_CSV):
        existing_steps.append(2)
    if os.path.exists(EMAILS_CSV):
        existing_steps.append(3)
    if os.path.exists(SUMMARIES_CSV):
        existing_steps.append(4)

    if existing_steps:
        print("Detected saved data for steps:", existing_steps)
        for step_num in existing_steps:
            print(f"Step {step_num}: {steps[step_num]}")
        while True:
            try:
                resume_step = int(
                    input(f"Enter the step number to resume from (1-{len(steps)}), or 0 to start over: ").strip()
                )
                if 0 <= resume_step <= len(steps):
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a valid step number or 0.")

        if resume_step == 0:
            for file in [PROFILE_URLS_CSV, METADATA_CSV, EMAILS_CSV, SUMMARIES_CSV, INPUT_PARAMS_JSON]:
                if os.path.exists(file):
                    os.remove(file)
            resume_step = 1
    else:
        resume_step = 1

    # Step 1
    if resume_step <= 1:
        linkedin_search_base_url = input("Enter the base LinkedIn search URL (e.g., https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22104738515%22%5D&keywords=electronics&origin=FACETED_SEARCH&page=): ").strip()

        while True:
            try:
                max_pages = int(input("Enter the number of pages to scrape: ").strip())
                break
            except ValueError:
                print("Please enter a valid integer for max_pages.")

        company_item_css = input("Enter the CSS selector for company items (e.g., li.rzkLCICBGYLAzTnzfmtIEgVSqcpg): ").strip()

        company_link_css = input("Enter the CSS selector for company links (e.g., a.pRsNlddsWvfIvSJxKEVQiVsNRgFbtHIxck): ").strip()
        lang = input("Enter the language for summaries (e.g., 'en' or 'fr'): ").strip().lower()

        input_params = {
            "linkedin_search_base_url": linkedin_search_base_url,
            "max_pages": max_pages,
            "company_item_css": company_item_css,
            "company_link_css": company_link_css,
            "lang": lang,
        }

        save_input_params(INPUT_PARAMS_JSON, input_params)

        print(f"Step 1: {steps[1]} ...")
        profile_urls = scrape_linkedin_company_profiles(
            linkedin_search_base_url, max_pages, company_item_css, company_link_css
        )
        print(f"Collected {len(profile_urls)} company profile URLs.")
        save_list_to_csv(PROFILE_URLS_CSV, profile_urls)

    else:
        input_params = load_input_params(INPUT_PARAMS_JSON)
        linkedin_search_base_url = input_params["linkedin_search_base_url"]
        max_pages = input_params["max_pages"]
        company_item_css = input_params["company_item_css"]
        company_link_css = input_params["company_link_css"]
        lang = input_params["lang"]

        profile_urls = load_list_from_csv(PROFILE_URLS_CSV)
        print(f"Loaded {len(profile_urls)} company profile URLs from saved data.")

    # Step 2
    if resume_step <= 2:
        print(f"Step 2: {steps[2]} ...")
        company_names, company_websites, company_about_texts = extract_company_metadata(profile_urls)
        save_metadata(METADATA_CSV, company_names, company_websites, company_about_texts)
    else:
        company_names, company_websites, company_about_texts = load_metadata(METADATA_CSV)
        print(f"Loaded metadata for {len(company_names)} companies from saved data.")

    # Step 3
    if resume_step <= 3:
        print(f"Step 3: {steps[3]} ...")
        emails = extract_contact_emails(company_websites)
        save_list_to_csv(EMAILS_CSV, emails)
    else:
        emails = load_list_from_csv(EMAILS_CSV)
        print(f"Loaded {len(emails)} emails from saved data.")

    # Step 4
    if resume_step <= 4:
        print(f"Step 4: {steps[4]} ...")
    
        # Préparer les textes valides et leur index
        valid_texts = []
        valid_indexes = []
        for i, (email, about_text) in enumerate(zip(emails, company_about_texts)):
            if email.strip():
                valid_texts.append(about_text)
                valid_indexes.append(i)
    
        # Générer les résumés uniquement pour les entrées avec email non vide
        if valid_texts:
            generated_summaries = generate_summaries(valid_texts, lang=lang)
        else:
            generated_summaries = []
    
        # Réinsérer les résumés aux bons index, sinon chaîne vide
        summaries = ["" for _ in company_about_texts]
        for idx, summary in zip(valid_indexes, generated_summaries):
            summaries[idx] = summary
    
        save_list_to_csv(SUMMARIES_CSV, summaries)
    else:
        summaries = load_list_from_csv(SUMMARIES_CSV)
        print(f"Loaded {len(summaries)} summaries from saved data.")


    # Step 5
    print(f"Step 5: {steps[5]} ...")
    export_to_spreadsheet(company_names, summaries, emails, folder=DATA_DIR)
    print("Export complete.")


if __name__ == "__main__":
    main()
