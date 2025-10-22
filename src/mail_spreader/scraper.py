import urllib
import yaml
import json
import importlib.resources
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

duration = 15

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

def is_linkedin_profile_url(url: str) -> bool:
    """
    Validate if the URL corresponds to a LinkedIn personal or company profile.
    """
    linkedin_profile_pattern = r"^https://www\.linkedin\.com/(in|company)/[^/]+/?$"
    return bool(re.match(linkedin_profile_pattern, url))

def print_progress_bar(iteration: int, total: int, prefix: str = "", bar_length: int = 50) -> None:
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})", end="", flush=True)
    if iteration == total:
        print()


def linkedin_url_creator(yaml_file_industries, yaml_file_url="linkedin_url.yaml"):
    """Use LinkedIn URL to make a YAML file containing a LinkedIn company profile search URL"""
    with open(yaml_file_industries, "r", encoding="utf-8") as f:
        config_industries = yaml.safe_load(f)

    # Load industry ID mappings directly from the installed package
    with importlib.resources.files("mail_spreader").joinpath("industries_ids.json").open("r", encoding="utf-8") as mf:
        mappings_list = json.load(mf)

    value_to_id = {item["value"]: item["id"] for item in mappings_list}
    list_industries = config_industries.get("list_industries", "")

    industry_ids = []
    for name in list_industries:
        id_val = value_to_id.get(name)
        if id_val is None:
            print(f"Warning: no mapping found for '{name}'")
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


def linkedin_list_urls_creator(yaml_file_industries, yaml_file_url="linkedin_url.yaml"):
    """Create a list of LinkedIn company search URLs, one for each industry"""

    with open(yaml_file_industries, "r", encoding="utf-8") as f:
        config_industries = yaml.safe_load(f)

    # Load the industry ID mappings from inside the package
    with importlib.resources.files("mail_spreader").joinpath("industries_ids.json").open("r", encoding="utf-8") as mf:
        mappings_list = json.load(mf)

    value_to_id = {item["value"]: item["id"] for item in mappings_list}
    list_industries = config_industries.get("list_industries", [])

    urls = []
    for name in list_industries:
        id_val = value_to_id.get(name)
        if id_val is None:
            print(f"Warning: no mapping found for '{name}'")
            continue
        
        encoded_industry = urllib.parse.quote(json.dumps([str(id_val)]))
        url = (
            f"https://www.linkedin.com/search/results/companies/?"
            f"industryCompanyVertical={encoded_industry}"
            f"&origin=FACETED_SEARCH&sid=_ay"
        )
        urls.append(url)

    with open(yaml_file_url, "w", encoding="utf-8") as fy:
        yaml.dump({"search_urls": urls}, fy, allow_unicode=True)

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