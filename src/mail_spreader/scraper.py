import urllib
import yaml
import json
import re
from pathlib import Path
import re
import time
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

duration = 15

def print_progress_bar(iteration: int, total: int, prefix: str = "", bar_length: int = 50) -> None:
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})", end="", flush=True)
    if iteration == total:
        print()

def login(driver,email,password):
    driver.get("https://www.linkedin.com/checkpoint/lg/sign-in-another-account")
    print("Login starting...")

    time.sleep(duration)

    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys(email)

    
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, "button.btn__primary--large.from__button--floating")
    login_button.click()

    print("Login done!")

    time.sleep(duration)

def find_elements_with_text(driver):
    """
    Opens a page with undetected_chromedriver, searches for <a> and <li> containing a given text.
    """

    url="https://www.linkedin.com/search/results/companies/?keywords=aveltek&origin=SWITCH_SEARCH_VERTICAL&sid=6Fj"
    delay=2
    search_text="AvelTek"
    driver.get(url)
    time.sleep(delay)

    # Search within tags <a>
    a_elements = driver.find_elements(By.TAG_NAME, 'a')
    a_matches = [
        {
            'text': a.text.strip(),
            'classes': a.get_attribute("class").split()
        }
        for a in a_elements if search_text in a.text
    ]

    # Search within <li> tags
    li_elements = driver.find_elements(By.TAG_NAME, 'li')
    li_matches = [
        {
            'text': li.text.strip(),
            'classes': li.get_attribute("class").split()
        }
        for li in li_elements if search_text in li.text
    ]
    company_item_selector = li_matches[0]['classes'][0] if li_matches else None
    print("company_item_selector:", "li."+company_item_selector)

    company_link_selector = a_matches[0]['classes'][0] if a_matches else None
    print("company_link_selector:", "a."+company_link_selector)

    # Return results
    return {
        'a_tags': a_matches,
        'li_tags': li_matches
    }


def linkedin_url_creator(yaml_file_industries, yaml_file_url="linkedin_url.yaml"):
    """Use LinkedinIn url to make a JSON of LinkedIn company profile URLs"""
    with open(yaml_file_industries, "r", encoding="utf-8") as f:
        config_industries = yaml.safe_load(f)

    mapping_file = "industries_ids.json"
    with open(mapping_file, "r", encoding="utf-8") as mf:
        mappings_list = json.load(mf)

    value_to_id = {item["value"]: item["id"] for item in mappings_list}
    list_industries = config_industries.get("list_industries", "")

    industry_ids = []
    for name in list_industries:
        id_val = value_to_id.get(name)
        if id_val is None:
            print(f"Warning: pas de mapping pour '{name}'")
        else:
            industry_ids.append(str(id_val))

    encoded_industry = urllib.parse.quote(json.dumps(industry_ids))

    url = (
        f"https://www.linkedin.com/search/results/companies/?"
        f"industryCompanyVertical={encoded_industry}"
        f"&origin=FACETED_SEARCH&sid=_ay"
    )

    with open(yaml_file_url, "w", encoding="utf-8") as fy:
        fy.write("base_search_url: " + json.dumps(url) + "\n")

def scrape_linkedin_company_profiles(yaml_file, json_file="collected_profile_urls.json"):
    """Use LinkedinIn url to make a JSON of LinkedIn company profile URLs"""
    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    base_search_url = config.get("base_search_url", "")
    total_pages = config.get("total_pages", 1)
    linkedin_email = config.get("linkedin_email", "")
    linkedin_password = config.get("linkedin_password", "")

    collected_profile_urls = []
    paginated_urls = [f"{base_search_url}{page}" for page in range(1, total_pages + 1)]

    options = uc.ChromeOptions()
    options.headless = True
    # Explicitly set Chrome binary location (update path if needed)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=options, browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")

    login(driver, linkedin_email,linkedin_password)

    results = find_elements_with_text(driver)
    company_item_selector = "li."+results['li_tags'][0]['classes'][0] if results['li_tags'] else None
    company_link_selector = "a."+results['a_tags'][0]['classes'][0] if results['a_tags'] else None

    try:
        for page_index, url in enumerate(paginated_urls, start=1):
            driver.get(url)
            time.sleep(duration)  # Adjust wait as necessary for page load

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

    data = {
        "collected_profile_urls": collected_profile_urls
    }

    # Sauvegarder en JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_linkedin_profile_url(url: str) -> bool:
    """
    Validate if the URL corresponds to a LinkedIn personal or company profile.
    """
    linkedin_profile_pattern = r"^https://www\.linkedin\.com/(in|company)/[^/]+/?$"
    return bool(re.match(linkedin_profile_pattern, url))

def extract_company_metadata(yaml_file, json_file_profil, json_file_metadata="metadata.json"):
    """Extract company names, websites, and about section text from LinkedIn profiles."""
    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Récupérer les variables
    linkedin_email = config.get("linkedin_email", "")
    linkedin_password = config.get("linkedin_password", "")

    company_names = []
    company_websites = []
    company_about_texts = []

    options = uc.ChromeOptions()
    options.headless = True
    driver = uc.Chrome(options=options)

    login(driver,linkedin_email,linkedin_password)

    with open(json_file_profil, "r", encoding="utf-8") as f:
        data = json.load(f)

    profile_urls = data.get("collected_profile_urls", [])
    
    try:
        for idx, profile_url in enumerate(profile_urls, start=1):
            profile_url = profile_url.strip()
            if not is_linkedin_profile_url(profile_url):
                continue

            about_page_url = profile_url.rstrip("/") + "/about/"
            driver.get(about_page_url)
            time.sleep(duration)  # Adjust wait as necessary for page load

            # Extract company name (from <h1>)
            try:
                heading_element = driver.find_element(By.TAG_NAME, "h1")
                company_names.append(heading_element.text)
            except NoSuchElementException:
                company_names.append("")

            # Extract company website URL
            try:
                website_dd = driver.find_element(By.CSS_SELECTOR, "dd.mb4.t-black--light.text-body-medium")
                website_link = website_dd.find_element(By.CSS_SELECTOR, "a.link-without-visited-state")
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

            print_progress_bar(iteration=idx, total=len(profile_urls), prefix="Extraction Progress:")
    finally:
        driver.quit()

    data = {
        "company_names": company_names,
        "company_websites": company_websites,
        "company_about_texts": company_about_texts
    }

    with open(json_file_metadata, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
