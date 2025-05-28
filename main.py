from mailspreader.linkedin_scraper import scrape_linkedin_company_profiles, extract_company_metadata
from mailspreader.website_parser import extract_emails
from mailspreader.summarizer import generate_summaries
from mailspreader.exporter import export_to_spreadsheet


def main() -> None:
    """
    Orchestrate the LinkedIn company data extraction and export process.
    """

    # Base URL template for LinkedIn company search with geo filter and keyword
    linkedin_search_base_url = (
        "https://www.linkedin.com/search/results/companies/"
        "?companyHqGeo=%5B%22104738515%22%5D&keywords=electronics&origin=FACETED_SEARCH&page="
    )
    max_pages = 3

    # CSS selectors to identify company items and links within search results
    company_item_css = "li.WDvdZYkmofkIebRhLNrkOumCFOUtZbbQg"
    company_link_css = "a.ieNkhTGfrWOzSPfkCJfKdgTOwrMDnOQ"

    # Step 1: Gather company profile URLs from paginated LinkedIn search results
    collected_profile_urls = scrape_linkedin_company_profiles(
        linkedin_search_base_url, max_pages, company_item_css, company_link_css
    )
    print(f"Collected {len(collected_profile_urls)} company profile URLs.")

    # Step 2: Extract company metadata (names, websites, about info)
    company_names, company_websites, company_about_texts = extract_company_metadata(collected_profile_urls)

    # Step 3: Retrieve contact emails from company websites
    emails = extract_emails(company_websites)

    # Step 4: Generate polished summaries for company descriptions
    # summaries = generate_summaries(about_sections)

    # Step 5: Export compiled data to spreadsheet format for Thunderbird
    # export_to_spreadsheet(names, summaries, emails)


if __name__ == "__main__":
    main()
