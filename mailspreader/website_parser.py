import undetected_chromedriver as uc
from urllib.parse import urlparse
import time
import re

def print_progress_bar(iteration: int, total: int, prefix: str = "", bar_length: int = 50) -> None:
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})", end="", flush=True)
    if iteration == total:
        print()

def is_google_captcha_url(url: str) -> bool:
    return url.startswith("https://www.google.com/sorry/index?continue=")

def handle_manual_captcha(driver):
    if is_google_captcha_url(driver.current_url):
        print("[!] CAPTCHA Google détecté.")
        print("Veuillez le résoudre dans le navigateur, puis appuyez sur Entrée ici pour continuer...")
        input()

def extract_contact_emails(website_urls: list[str]) -> list[str]:
    extracted_emails = []

    options = uc.ChromeOptions()
    options.headless = False

    driver = uc.Chrome(options=options)
    driver.get("https://www.google.com")
    handle_manual_captcha(driver)

    def extract_email_from_text(text: str) -> str:
        hr_email_match = re.search(r"hr@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text, re.IGNORECASE)
        if hr_email_match:
            return hr_email_match.group(0)

        email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
        matches = email_regex.findall(text)

        if not matches:
            obf_regex = re.compile(r"([a-zA-Z0-9._%+-]+)\s*<at>\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", re.IGNORECASE)
            obf_matches = obf_regex.findall(text)
            matches = [f"{m[0]}@{m[1]}" for m in obf_matches]

        if not matches:
            return ""

        filtered = [e for e in matches if "sales" not in e.lower() and "@www." not in e.lower()]
        if filtered:
            return filtered[0]

        non_www = [e for e in matches if "@www." not in e.lower()]
        if non_www:
            return non_www[0]

        return matches[0]

    for i in range(len(website_urls)):
        normalized_url = website_urls[i] if website_urls[i].startswith(("http://", "https://")) else f"http://{website_urls[i]}"
        parsed_url = urlparse(normalized_url)
        netloc_with_www = parsed_url.netloc.split(':')[0]
        netloc_no_www = re.sub(r"^www\.", "", netloc_with_www)

        found_email = ""

        # Étape 1 : /contact/
        for scheme in ["https", "http"]:
            contact_url = f"{scheme}://{netloc_with_www}/contact/"
            try:
                driver.get(contact_url)
                time.sleep(5)
                contact_text = driver.find_element("tag name", "body").text
                found_email = extract_email_from_text(contact_text)
                if found_email:
                    break
            except Exception:
                continue

        email_is_sales = "sales" in found_email.lower() if found_email else False

        # Étape 1.5 : Google "hr@" si sales ou @www
        if found_email and (email_is_sales or "@www." in found_email.lower()):
            try:
                google_query = f'"{netloc_no_www} hr @"'
                driver.get(f"https://www.google.com/search?q={google_query}")
                handle_manual_captcha(driver)
                time.sleep(10)
                page_text = driver.find_element("tag name", "body").text
                hr_email = extract_email_from_text(page_text)
                if hr_email and "sales" not in hr_email.lower() and "@www." not in hr_email.lower():
                    found_email = hr_email
                    email_is_sales = False
            except Exception:
                pass

        # Étape 2 : Google "career @{domain}"
        if not found_email or email_is_sales or "@www." in found_email.lower():
            try:
                google_query = f'"career @{netloc_no_www}"'
                driver.get(f"https://www.google.com/search?q={google_query}")
                handle_manual_captcha(driver)
                time.sleep(10)
                page_text = driver.find_element("tag name", "body").text
                alt_email = extract_email_from_text(page_text)
                if alt_email and "sales" not in alt_email.lower() and "@www." not in alt_email.lower():
                    found_email = alt_email
                    email_is_sales = False
            except Exception:
                pass

        # Étape 3 : Fallback Google
        if not found_email or email_is_sales or "@www." in found_email.lower():
            fallback_queries = [f'intext:"@{netloc_no_www}"', f'"@{netloc_no_www}"']
            for query in fallback_queries:
                try:
                    driver.get(f"https://www.google.com/search?q={query}")
                    handle_manual_captcha(driver)
                    time.sleep(10)
                    page_text = driver.find_element("tag name", "body").text
                    alt_email = extract_email_from_text(page_text)
                    if alt_email and "sales" not in alt_email.lower() and "@www." not in alt_email.lower():
                        found_email = alt_email
                        break
                except Exception:
                    continue

        extracted_emails.append(found_email)
        print_progress_bar(iteration=i+1, total=len(website_urls), prefix="Extract email Progress:")

    driver.quit()
    return extracted_emails
