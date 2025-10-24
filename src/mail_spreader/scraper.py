import urllib
import yaml
import json
import importlib.resources
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psutil

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

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

def extract_company_metadata(yaml_file, json_file_profil, json_file_metadata="metadata.json"):
    """Extract company names, websites, and about section text from LinkedIn profiles with retry and timeout handling."""

    MAX_PAGE_RETRIES = 3
    MAX_DRIVER_RETRIES = 5
    PAGE_LOAD_TIMEOUT = 45
    SLEEP_BETWEEN_RETRIES = 10
    WAIT_BETWEEN_PAGES = 5

    def cleanup_chrome():
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and "chrome" in proc.info['name'].lower():
                    proc.terminate()
            except Exception:
                pass

    def create_driver():
        cleanup_chrome()
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        try:
            driver = uc.Chrome(
                options=options,
                version_main=141,
                browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            )
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            return driver
        except Exception as e:
            print(f"[ERROR] Failed to create driver: {e}")
            raise

    def safe_get(driver, url):
        for attempt in range(1, MAX_DRIVER_RETRIES + 1):
            try:
                driver.get(url)
                return driver
            except (TimeoutException, WebDriverException) as e:
                print(f"[WARN] Driver error on {url} (attempt {attempt}/{MAX_DRIVER_RETRIES}): {e}")
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(SLEEP_BETWEEN_RETRIES)
                try:
                    driver = create_driver()
                    login(driver, linkedin_email, linkedin_password)
                except Exception as e2:
                    print(f"[ERROR] Failed to restart driver: {e2}")
                continue
        print(f"[ERROR] Skipping {url} after {MAX_DRIVER_RETRIES} failed driver attempts.")
        return driver

    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    linkedin_email = config.get("linkedin_email", "")
    linkedin_password = config.get("linkedin_password", "")

    with open(json_file_profil, "r", encoding="utf-8") as f:
        data = json.load(f)
    profile_urls = data.get("collected_profile_urls", [])

    company_names = []
    company_websites = []
    company_about_texts = []

    driver = create_driver()
    login(driver, linkedin_email, linkedin_password)

    try:
        for idx, profile_url in enumerate(profile_urls, start=1):
            profile_url = profile_url.strip()
            if not is_linkedin_profile_url(profile_url):
                continue

            about_page_url = profile_url.rstrip("/") + "/about/"

            success = False
            for attempt in range(1, MAX_PAGE_RETRIES + 1):
                try:
                    driver = safe_get(driver, about_page_url)
                    time.sleep(WAIT_BETWEEN_PAGES)

                    try:
                        heading_element = driver.find_element(By.TAG_NAME, "h1")
                        company_names.append(heading_element.text)
                    except NoSuchElementException:
                        company_names.append("")

                    try:
                        website_dd = driver.find_element(By.CSS_SELECTOR, "dd.mb4.t-black--light.text-body-medium")
                        website_link = website_dd.find_element(By.CSS_SELECTOR, "a.link-without-visited-state")
                        company_websites.append(website_link.get_attribute("href"))
                    except NoSuchElementException:
                        company_websites.append("")

                    try:
                        about_paragraph = driver.find_element(
                            By.CSS_SELECTOR,
                            "p.break-words.white-space-pre-wrap.t-black--light.text-body-medium",
                        )
                        company_about_texts.append(about_paragraph.text)
                    except NoSuchElementException:
                        company_about_texts.append("")

                    success = True
                    break

                except Exception as e:
                    print(f"[WARN] Attempt {attempt}/{MAX_PAGE_RETRIES} failed for {about_page_url}: {e}")
                    time.sleep(SLEEP_BETWEEN_RETRIES)
                    if attempt == MAX_PAGE_RETRIES:
                        print(f"[ERROR] Skipping {about_page_url} after repeated failures.")
                        company_names.append("")
                        company_websites.append("")
                        company_about_texts.append("")
                        try:
                            driver.quit()
                        except Exception:
                            pass
                        driver = create_driver()
                        login(driver, linkedin_email, linkedin_password)

            print_progress_bar(
                iteration=idx,
                total=len(profile_urls),
                prefix="Extraction Progress:",
                bar_length=40
            )

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    data = {
        "company_names": company_names,
        "company_websites": company_websites,
        "company_about_texts": company_about_texts
    }
    with open(json_file_metadata, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Results written to {json_file_metadata}")



def get_total_pages_for_url(driver, base_url, delay=3):
    """
    Ouvre une page avec undetected_chromedriver et retourne
    le plus grand numéro de page trouvé dans la pagination.
    """
    driver.get(base_url)
    time.sleep(delay)  # attendre que le JS charge le contenu

    # Récupérer tous les <li> ayant l'attribut data-test-pagination-page-btn
    li_elements = driver.find_elements(By.CSS_SELECTOR, "li[data-test-pagination-page-btn]")

    # Extraire les valeurs numériques
    page_numbers = []
    for li in li_elements:
        val = li.get_attribute("data-test-pagination-page-btn")
        if val and val.isdigit():
            page_numbers.append(int(val))

    # Retourner la valeur maximale
    return max(page_numbers) if page_numbers else None




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

def scrape_linkedin_company_profiles(yaml_file, json_file):
    """Scrape LinkedIn company profiles with retry, driver restart, process cleanup, and deduplication."""
    import json, time, yaml, psutil, signal
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

    MAX_PAGE_RETRIES = 3
    MAX_DRIVER_RETRIES = 5
    PAGE_LOAD_TIMEOUT = 45
    SLEEP_BETWEEN_RETRIES = 10

    collected_profile_urls = []

    # -------------------------------------------------------
    # Utilitaires
    # -------------------------------------------------------

    def cleanup_chrome():
        """Tuer tous les processus Chrome pour repartir propre."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and "chrome" in proc.info['name'].lower():
                    proc.terminate()
            except Exception:
                pass

    def create_driver():
        """Créer un driver propre avec timeout défini."""
        cleanup_chrome()
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        try:
            driver = uc.Chrome(
                options=options,
                version_main=141,
                browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            )
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            return driver
        except Exception as e:
            print(f"[ERROR] Failed to create driver: {e}")
            raise

    def safe_get(driver, url):
        """Tente de charger une page avec plusieurs essais et recrée le driver si nécessaire."""
        for attempt in range(1, MAX_DRIVER_RETRIES + 1):
            try:
                driver.get(url)
                return driver
            except (TimeoutException, WebDriverException) as e:
                print(f"[WARN] Driver error on {url} (attempt {attempt}/{MAX_DRIVER_RETRIES}): {e}")
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(SLEEP_BETWEEN_RETRIES)
                try:
                    driver = create_driver()
                    login(driver, linkedin_email, linkedin_password)
                except Exception as e2:
                    print(f"[ERROR] Failed to restart driver: {e2}")
                continue
        print(f"[ERROR] Skipping {url} after {MAX_DRIVER_RETRIES} failed driver attempts.")
        return driver

    # -------------------------------------------------------
    # Lecture de la configuration
    # -------------------------------------------------------

    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    linkedin_email = config.get("linkedin_email", "")
    linkedin_password = config.get("linkedin_password", "")
    base_search_urls = config.get("base_search_url", [])
    duration = config.get("duration", 5)

    if isinstance(base_search_urls, str):
        base_search_urls = [base_search_urls]

    driver = create_driver()
    login(driver, linkedin_email, linkedin_password)

    results = find_elements_with_text(driver)
    company_item_selector = "li." + results['li_tags'][0]['classes'][0] if results['li_tags'] else None
    company_link_selector = "a." + results['a_tags'][0]['classes'][0] if results['a_tags'] else None

    # -------------------------------------------------------
    # Boucle principale de scraping
    # -------------------------------------------------------

    try:
        for base_search_url in base_search_urls:
            print(f"\nProcessing base search URL: {base_search_url}")

            total_pages = get_total_pages_for_url(driver, base_search_url, duration)
            if not total_pages:
                print("[WARN] Could not determine total pages for this URL.")
                continue

            paginated_urls = [f"{base_search_url}&page={page}" for page in range(1, total_pages + 1)]

            for page_index, url in enumerate(paginated_urls, start=1):
                success = False
                scraped_this_page = 0

                try:
                    for attempt in range(1, MAX_PAGE_RETRIES + 1):
                        driver = safe_get(driver, url)
                        time.sleep(duration)

                        try:
                            company_elements = driver.find_elements(By.CSS_SELECTOR, company_item_selector)
                        except NoSuchElementException:
                            company_elements = []

                        count_before = len(collected_profile_urls)
                        for element in company_elements:
                            try:
                                link_element = element.find_element(By.CSS_SELECTOR, company_link_selector)
                                href = link_element.get_attribute("href")
                                if href:
                                    collected_profile_urls.append(href)
                            except NoSuchElementException:
                                continue

                        scraped_this_page = len(collected_profile_urls) - count_before

                        if scraped_this_page > 0:
                            success = True
                            break
                        else:
                            print(f"[WARN] Page {page_index}: 0 results, retry {attempt}/{MAX_PAGE_RETRIES}...")
                            time.sleep(SLEEP_BETWEEN_RETRIES)

                            if attempt == MAX_PAGE_RETRIES:
                                print(f"[INFO] Restarting driver after empty results on page {page_index}.")
                                try:
                                    driver.quit()
                                except Exception:
                                    pass
                                driver = create_driver()
                                login(driver, linkedin_email, linkedin_password)
                                try:
                                    driver = safe_get(driver, url)
                                    time.sleep(duration)
                                    company_elements = driver.find_elements(By.CSS_SELECTOR, company_item_selector)
                                    count_after = len(collected_profile_urls)
                                    if count_after == count_before:
                                        print(f"[ERROR] Page {page_index}: still no results after retries and driver restart.")
                                    else:
                                        success = True
                                        break
                                except Exception as e:
                                    print(f"[FATAL] safe_get failed on retry for page {page_index}: {e}")
                                    break

                except Exception as e:
                    print(f"[FATAL] Exception during scraping page {page_index}: {e}")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = create_driver()
                    login(driver, linkedin_email, linkedin_password)
                    continue

                if not success:
                    print(f"[WARN] Skipping page {page_index} for {base_search_url} after multiple failures.")

                print_progress_bar(
                    iteration=page_index,
                    total=total_pages,
                    prefix=f"Scraping Progress (Current URL): |  Data scraped this page: {scraped_this_page}",
                    bar_length=40
                )

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    # -------------------------------------------------------
    # Nettoyage final (suppression des doublons)
    # -------------------------------------------------------

    collected_profile_urls = list(dict.fromkeys(collected_profile_urls))
    print(f"[INFO] Deduplicated URLs count: {len(collected_profile_urls)}")

    data = {"collected_profile_urls": collected_profile_urls}
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Results written to {json_file}")
