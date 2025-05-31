from mailspreader.linkedin_scraper import scrape_linkedin_company_profiles, extract_company_metadata
from mailspreader.website_parser import extract_contact_emails
from mailspreader.summarizer import generate_summaries
from mailspreader.exporter import export_to_spreadsheet


def main() -> None:
    """
    Orchestrate the LinkedIn company data extraction and export process.
    """

    # Input parameters
    linkedin_search_base_url = input(
        "Enter the base LinkedIn search URL (e.g., https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22104738515%22%5D&keywords=electronics&origin=FACETED_SEARCH&page=): "
    ).strip()

    while True:
        try:
            max_pages = int(input("Enter the number of pages to scrape: ").strip())
            break
        except ValueError:
            print("Please enter a valid integer for max_pages.")

    company_item_css = input("Enter the CSS selector for company items: ").strip()
    company_link_css = input("Enter the CSS selector for company links: ").strip()
    lang = input("Enter the language for summaries (e.g., 'en' or 'fr'): ").strip().lower()

    # Step 1: Gather company profile URLs from paginated LinkedIn search results
    collected_profile_urls = scrape_linkedin_company_profiles(
        linkedin_search_base_url, max_pages, company_item_css, company_link_css
    )
    print(f"Collected {len(collected_profile_urls)} company profile URLs.")

    # Step 2: Extract company metadata (names, websites, about info)
    company_names, company_websites, company_about_texts = extract_company_metadata(collected_profile_urls)

    # Step 3: Retrieve contact emails from company websites
    emails = extract_contact_emails(company_websites)

    # Step 4: Generate polished summaries for company descriptions
    summaries = generate_summaries(company_about_texts)
    
    # Step 5: Export compiled data to spreadsheet format for Thunderbird
    export_to_spreadsheet(company_names, summaries, emails)

if __name__ == "__main__":
    main()
