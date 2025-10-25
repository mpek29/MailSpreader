import undetected_chromedriver as uc
from urllib.parse import urlparse
import time
import re
import json
import random
from .utils import build_google_search_url, DEFAULT_USER_AGENT_POOL
import socket
import typer
import os
import webbrowser

def is_google_captcha_url(url: str) -> bool:
    return url.startswith("https://www.google.com/sorry/index?continue=")

def handle_manual_captcha(driver):
    if is_google_captcha_url(driver.current_url):
        print("[!] Google CAPTCHA detected.")
        print("Please solve it in the browser, then press Enter here to continue...")
        input()
        
def print_progress_bar(iteration: int, total: int, prefix: str = "", bar_length: int = 50) -> None:
    progress_fraction = iteration / total
    filled_length = int(bar_length * progress_fraction)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percent = progress_fraction * 100
    print(f"\r{prefix} |{bar}| {percent:6.2f}% ({iteration}/{total})", end="", flush=True)
    if iteration == total:
        print()

def extract_contact_emails_manual(json_file_metadata, json_file_email="email.json"):
    with open(json_file_metadata, "r", encoding="utf-8") as f:
        data = json.load(f)

    website_urls = data.get("company_websites", [])

    extracted_emails = []

    options = uc.ChromeOptions()
    options.headless = False

    driver = uc.Chrome(options=options)
    driver.get("https://www.google.com")
    handle_manual_captcha(driver)

    for i in range(len(website_urls)):
        url = website_urls[i]
        normalized_url = url if url.startswith(("http://", "https://")) else f"http://{url}"
        parsed_url = urlparse(normalized_url)
        netloc_with_www = parsed_url.netloc.split(':')[0]
        netloc_no_www = re.sub(r"^www\.", "", netloc_with_www)

        found_email = []
        
        # Étape 1 : Fallback Google
        fallback_queries = f'intext:"@{netloc_no_www}"'
        try:
            driver.get(f"https://www.google.com/search?q={fallback_queries}")
            handle_manual_captcha(driver)
            new_found_email = input('Email trouvé sur Google ? (email/n) : ').strip()
            if new_found_email!="n" or new_found_email!="N":
                found_email.append(new_found_email)
                
        except Exception:
            pass

        # Étape 2 : Website
        try:
            driver.get(website_urls[i])
            new_found_email = input('Email trouvé sur le site ? (email/n) : ').strip()
            if new_found_email!="n" or new_found_email!="N":
                found_email.append(new_found_email)
                
        except Exception:
            pass

        extracted_emails.append(found_email)
        print_progress_bar(iteration=i+1, total=len(website_urls), prefix="Extract email Progress:")

    driver.quit()

    data = {
        "extracted_emails": extracted_emails
    }

    with open(json_file_email, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Driver avec proxy et user-agent
def start_driver_with_proxy(proxy_url=None, headless=False, user_agent=None):
    options = uc.ChromeOptions()
    options.headless = headless
    if proxy_url:
        options.add_argument(f"--proxy-server={proxy_url}")
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    return uc.Chrome(options=options)



def test_proxy(ip, port, timeout=3):
    try:
        s = socket.create_connection((ip, int(port)), timeout)
        s.close()
        return True
    except:
        return False


# Création d’un pool de drivers
def build_driver_pool(proxies, max_pool_size=6, headless=False, user_agent_pool=None):
    # Filtrer les proxies morts avant de lancer les drivers
    valid_proxies = []
    for p in proxies:
        ip_port = p.split(":")  # supposons format "IP:Port"
        if test_proxy(ip_port[0], ip_port[1]):
            valid_proxies.append(p)
        else:
            print(f"[!] Proxy mort ou inaccessible : {p}")

    pool_size = min(len(valid_proxies), max_pool_size)
    drivers = []
    for i in range(pool_size):
        proxy = valid_proxies[i % len(valid_proxies)]
        ua = None
        if user_agent_pool:
            ua = user_agent_pool[i % len(user_agent_pool)]
        drv = start_driver_with_proxy(proxy, headless=headless, user_agent=ua)
        drv.get("https://www.google.com")
        time.sleep(1.5)
        drivers.append(drv)
    return drivers

def extract_contact_emails_auto(
    json_file_metadata,
    json_file_email="email.json",
    include_tracking_in_search=True,
    rotate_clients=True,
    client_pool=None,
    proxies=None,
    user_agent_pool=None,
    requests_per_minute=30,
    min_delay=3,
    max_delay=8,
    max_driver_pool_size=6,
    headless=False
):
    if client_pool is None:
        client_pool = [
            # Desktop Chrome Windows
            "firefox-b-d",
            "chrome-iso",
            "chrome-b-d",
            "chrome-win",
            "chrome-mac",
            "firefox-win",
            "firefox-mac",

            # Mobile Chrome / Firefox / Safari
            "chrome-android",
            "firefox-android",
            "safari-ios",
            "edge-android",
            "edge-ios",

            # Desktop Edge / Opera
            "edge-win",
            "edge-mac",
            "opera-win",
            "opera-mac",

            # Variantes Linux
            "chrome-linux",
            "firefox-linux",

            # Nouveaux UA aléatoires
            "chrome-win-legacy",
            "chrome-mac-legacy",
            "firefox-win-legacy",
            "firefox-linux-legacy",
        ]

    if proxies is None:
        proxies = []
    if user_agent_pool is None:
        user_agent_pool = DEFAULT_USER_AGENT_POOL

    # Limitation du taux de requêtes
    min_interval = 60.0 / requests_per_minute if requests_per_minute > 0 else 0
    last_request_time = 0

    def ensure_rate_limit():
        nonlocal last_request_time
        elapsed = time.time() - last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed + random.uniform(0, 0.5))
        last_request_time = time.time()

    # Création du pool de drivers
    if proxies:
        driver_pool = build_driver_pool(
            proxies,
            max_pool_size=max_driver_pool_size,
            headless=headless,
            user_agent_pool=user_agent_pool,
        )
    else:
        drv = start_driver_with_proxy(
            None, headless=headless, user_agent=random.choice(user_agent_pool)
        )
        drv.get("https://www.google.com")
        driver_pool = [drv]

    def get_driver_for_index(index):
        return driver_pool[index % len(driver_pool)]

    # Extraction d’un email depuis un texte
    def extract_email_from_text(text):
        hr = re.search(r"hr@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text, re.I)
        if hr:
            return hr.group(0)
        regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.I)
        matches = regex.findall(text)
        if not matches:
            obf = re.compile(
                r"([a-zA-Z0-9._%+-]+)\s*<at>\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", re.I
            )
            matches = [f"{m[0]}@{m[1]}" for m in obf.findall(text)]
        if not matches:
            return ""
        filtered = [
            e for e in matches if "sales" not in e.lower() and "@www." not in e.lower()
        ]
        return filtered[0] if filtered else matches[0]

    # Lecture du JSON d’entrée
    with open(json_file_metadata, "r", encoding="utf-8") as f:
        data = json.load(f)
    websites = data.get("company_websites", [])
    extracted = []

    # Recherche Google via driver
    def google_search_extract(driver, q, client=None):
        sel_client = client if client else random.choice(client_pool)
        url = build_google_search_url(
            q, client=sel_client, include_tracking=include_tracking_in_search
        )
        ensure_rate_limit()
        try:
            driver.get(url)
            handle_manual_captcha(driver)
            time.sleep(random.uniform(min_delay, max_delay))
            text = driver.find_element("tag name", "body").text
            return extract_email_from_text(text)
        except Exception:
            return ""

    # Boucle principale sur les sites
    for i, url in enumerate(websites):
        # --- Vérification stricte pour ignorer les entrées vides ---
        if url=="" or url.startswith("tel:"):
            extracted.append("")
            print_progress_bar(i + 1, len(websites))
            continue

        driver = get_driver_for_index(i)

        # Ignorer LinkedIn
        if "linkedin.com" in url.lower():
            extracted.append("")
            print_progress_bar(i + 1, len(websites))
            time.sleep(random.uniform(min_delay, max_delay))
            continue

        # Normalisation
        normalized = url if url.startswith(("http://", "https://")) else f"http://{url}"
        parsed = urlparse(normalized)
        netloc = re.sub(r"^www\.", "", parsed.netloc.split(":")[0])
        found_email = ""

        # Étape 1 : page /contact/
        for s in ["https", "http"]:
            try:
                if netloc:  # Sécurité supplémentaire
                    driver.get(f"{s}://{netloc}/contact/")
                    time.sleep(random.uniform(2, 5))
                    found_email = extract_email_from_text(
                        driver.find_element("tag name", "body").text
                    )
                    if found_email:
                        break
            except:
                pass

        # Étape 2 : recherche Google (fallback)
        if not found_email or "sales" in found_email.lower() or "@www." in found_email.lower():
            for q in [
                f'"{netloc} hr @"',
                f'"career @{netloc}"',
                f'intext:"@{netloc}"',
            ]:
                alt = google_search_extract(driver, q)
                if alt and "sales" not in alt.lower() and "@www." not in alt.lower():
                    found_email = alt
                    break

        extracted.append(found_email)
        print_progress_bar(i + 1, len(websites))
        time.sleep(random.uniform(min_delay, max_delay))

    # Fermeture des drivers
    for d in driver_pool:
        try:
            d.quit()
        except:
            pass

    # Sauvegarde JSON
    with open(json_file_email, "w", encoding="utf-8") as f:
        json.dump({"extracted_emails": extracted}, f, ensure_ascii=False, indent=2)

    return {"extracted_emails": extracted}


def merge_extracted_email_jsons(input_folder, output_file="merged_emails.json"):
    """
    Fusionne les fichiers emails_X.json dans l'ordre croissant de X.
    Conserve les chaînes vides et l'ordre d'origine.
    """
    # Récupérer les fichiers emails_X.json dans l'ordre numérique
    json_files = []
    for f in os.listdir(input_folder):
        match = re.match(r"emails_(\d+)\.json$", f)
        if match:
            index = int(match.group(1))
            json_files.append((index, f))
    json_files.sort(key=lambda x: x[0])

    merged_emails = []

    for index, filename in json_files:
        path = os.path.join(input_folder, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "extracted_emails" in data:
                merged_emails.extend(data["extracted_emails"])
            else:
                typer.echo(f"⚠️ {filename} ne contient pas de clé 'extracted_emails'")
        except Exception as e:
            typer.echo(f"⚠️ Erreur lors de la lecture de {filename}: {e}")

    # Ne pas supprimer les vides, ne pas dédupliquer
    output_path = os.path.join(input_folder, output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"extracted_emails": merged_emails}, f, ensure_ascii=False, indent=2)

    return {"extracted_emails": merged_emails, "output_file": output_path}

def extract_companies_without_email(metadata_file, email_file, output_file="companies_without_mail.json"):
    """
    Identifie les entreprises dont l'email est vide et enregistre leurs informations dans un JSON dédié.
    """
    # Lecture des fichiers d'entrée
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    with open(email_file, "r", encoding="utf-8") as f:
        emails = json.load(f)

    company_names = metadata.get("company_names", [])
    company_websites = metadata.get("company_websites", [])
    company_about = metadata.get("company_about_texts", [])
    extracted_emails = emails.get("extracted_emails", [])

    # Vérification de la cohérence des longueurs
    n = min(len(company_names), len(company_websites), len(company_about), len(extracted_emails))

    companies_without_mail = []
    for i in range(n):
        if extracted_emails[i] == "" and company_websites[i]:
            companies_without_mail.append({
                "name": company_names[i],
                "website": company_websites[i],
                "about": company_about[i],
                "email": extracted_emails[i],
            })

    # Sauvegarde du résultat
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"companies_without_email": companies_without_mail}, f, ensure_ascii=False, indent=2)

    return {"count": len(companies_without_mail), "output_file": output_file}


def manual_review_companies(input_file):
    """
    Permet de consulter manuellement les sites listés dans companies_without_mail.json,
    avec validation utilisateur avant de passer au suivant.
    """
    if not os.path.exists(input_file):
        typer.echo(f"❌ Fichier introuvable : {input_file}")
        raise typer.Exit(code=1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    companies = data.get("companies_without_email", [])
    if not companies:
        typer.echo("Aucune entreprise à consulter.")
        return

    typer.echo(f"📋 {len(companies)} entreprises à vérifier.")
    for i, company in enumerate(companies, 1):
        name = company.get("name", "Nom inconnu")
        site = company.get("website", "")
        typer.echo(f"\n[{i}/{len(companies)}] {name}")
        typer.echo(f"🔗 {site}")
        if site.startswith("http"):
            try:
                webbrowser.open(site)
            except Exception:
                typer.echo("⚠️ Impossible d’ouvrir le navigateur automatiquement.")

        input("Appuyez sur Entrée une fois que vous avez consulté le site...")

        # Pause de confort
        time.sleep(0.5)

    typer.echo("✅ Revue manuelle terminée.")
