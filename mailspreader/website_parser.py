import undetected_chromedriver as uc
from urllib.parse import urlparse
import time
import re

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

def extract_contact_emails(website_urls: list[str]) -> list[str]:
    """
    Extract emails associated with a list of company websites using Google search.

    Args:
        website_urls (list[str]): List of company website URLs.

    Returns:
        list[str]: List of extracted emails, one per website if found.
    """
    extracted_emails = []

    options = uc.ChromeOptions()
    options.headless = False  # Keep browser visible for manual login if needed

    driver = uc.Chrome(options=options)
    driver.get("https://www.google.com")
    input("Please complete any manual steps in the browser, then press Enter here to continue...")

    for i in range(len(website_urls)):
        normalized_url = website_urls[i] if website_urls[i].startswith(("http://", "https://")) else f"http://{website_urls[i]}"
        domain = urlparse(normalized_url).netloc.split(':')[0]  # Remove port if present

        if domain.startswith("www."):
            domain = domain[4:]

        search_query = f'intext:"@{domain}"'
        google_search_url = f"https://www.google.com/search?q={search_query}"

        driver.get(google_search_url)
        time.sleep(10)  # Allow time for the search results to load fully

        page_text = driver.find_element("tag name", "body").text
        email_regex = re.compile(rf"[a-zA-Z0-9._%+-]+@{re.escape(domain)}")

        found_emails = email_regex.findall(page_text)
        if found_emails:
            extracted_emails.append(found_emails[0])
        else:
            extracted_emails.append("")

        print_progress_bar(iteration=i, total=len(website_urls), prefix="Extract email Progress:", bar_length=len(website_urls))

    driver.quit()
    return extracted_emails
