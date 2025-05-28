import re
import sys
import time
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def is_linkedin_profile_url(url: str) -> bool:
    """
    Validate if the URL corresponds to a LinkedIn personal or company profile.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True if valid LinkedIn profile URL, False otherwise.
    """
    linkedin_profile_pattern = r"^https://www\.linkedin\.com/(in|company)/[^/]+/?$"
    return bool(re.match(linkedin_profile_pattern, url))


def print_progress_bar(
    iteration: int, total: int, prefix: str = "", bar_length: int = 50
) -> None:
    """
    Render a progress bar in the terminal.

    Args:
        iteration (int): Current iteration count (1-based).
        total (int): Total number of iterations.
        prefix (str): Optional string to prefix the progress bar.
        bar_length (int): Length of the progress bar in characters.
    """
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(
        f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})",
        end="",
        flush=True,
    )
    if iteration == total:
        print()


def scrape_linkedin_company_profiles(
    base_search_url: str,
    total_pages: int,
    company_item_selector: str,
    company_link_selector: str,
) -> list[str]:
    """
    Collect LinkedIn company profile URLs by iterating over paginated search results.

    Args:
        base_search_url (str): LinkedIn search URL prefix (without page number).
        total_pages (int): Number of pages to scrape.
        company_item_selector (str): CSS selector for company list items.
        company_link_selector (str): CSS selector for the link within each company item.

    Returns:
        list[str]: List of extracted company profile URLs.
    """
    collected_profile_urls = []
    paginated_urls = [f"{base_search_url}{page}" for page in range(1, total_pages + 1)]

    options = uc.ChromeOptions()
    options.headless = False  # Show browser to allow manual LinkedIn login
    driver = uc.Chrome(options=options)

    driver.get("https://www.linkedin.com")
    input("Please log into LinkedIn in the browser window, then press Enter here to continue...")

    try:
        for page_index, url in enumerate(paginated_urls, start=1):
            driver.get(url)
            time.sleep(15)  # Adjust wait as necessary for page load

            try:
                company_elements = driver.find_elements(By.CSS_SELECTOR, company_item_selector)
            except NoSuchElementException:
                company_elements = []

            for element in company_elements:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, company_link_selector)
                    href = link_element.get_attribute("href")
                    if href:
                        collected_profile_urls.append(href)
                except NoSuchElementException:
                    continue

            print_progress_bar(iteration=page_index, total=total_pages, prefix="Scraping Progress:", bar_length=40)
    finally:
        driver.quit()

    return collected_profile_urls


def extract_company_metadata(profile_urls: list[str]) -> tuple[list[str], list[str], list[str]]:
    """
    Extract company names, websites, and about section text from LinkedIn profiles.

    Args:
        profile_urls (list[str]): URLs of LinkedIn company profiles.

    Returns:
        tuple: Three lists containing company names, website URLs, and about texts.
    """
    company_names = []
    company_websites = []
    company_about_texts = []

    options = uc.ChromeOptions()
    options.headless = False  # Show browser to allow manual LinkedIn login
    driver = uc.Chrome(options=options)

    driver.get("https://www.linkedin.com")
    input("Please log into LinkedIn in the browser window, then press Enter here to continue...")

    try:
        for idx, profile_url in enumerate(profile_urls, start=1):
            profile_url = profile_url.strip()
            if not is_linkedin_profile_url(profile_url):
                continue

            about_page_url = profile_url.rstrip("/") + "/about/"
            driver.get(about_page_url)
            time.sleep(15)  # Adjust wait as necessary for page load

            # Extract company name (from <h1>)
            try:
                heading_element = driver.find_element(By.TAG_NAME, "h1")
                company_names.append(heading_element.text)
            except NoSuchElementException:
                company_names.append("")

            # Extract company website URL
            try:
                website_link = driver.find_element(By.CSS_SELECTOR, "a.link-without-visited-state")
                company_websites.append(website_link.get_attribute("href"))
            except NoSuchElementException:
                company_websites.append("")

            # Extract about section paragraph text
            try:
                about_paragraph = driver.find_element(
                    By.CSS_SELECTOR,
                    "p.break-words.white-space-pre-wrap.t-black--light.text-body-medium",
                )
                company_about_texts.append(about_paragraph.text)
            except NoSuchElementException:
                company_about_texts.append("")

            print_progress_bar(iteration=idx, total=len(profile_urls), prefix="Extraction Progress:", bar_length=40)
    finally:
        driver.quit()

    return company_names, company_websites, company_about_texts
