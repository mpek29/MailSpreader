import time
import random
import hashlib
import base64
import secrets
import struct
import zlib
from urllib.parse import quote_plus
from typing import List
import re

def random_hex(length=32):
    return secrets.token_hex((length + 1) // 2)[:length]

def make_ei(query):
    h = hashlib.sha1((query + str(time.time()) + str(random.getrandbits(64))).encode()).digest()
    return base64.urlsafe_b64encode(h)[:22].decode('ascii').rstrip('=')

def make_ved_plausible(query, result_index=0, click_type=0, client='firefox-b-d', version=1, ts=None):
    if ts is None:
        ts = int(time.time() * 1000)
    version_b = struct.pack(">B", int(version) & 0xFF)
    ts_b = struct.pack(">Q", int(ts) & ((1 << 64) - 1))
    result_b = struct.pack(">H", int(result_index) & 0xFFFF)
    click_b = struct.pack(">B", int(click_type) & 0xFF)
    client_hash = hashlib.sha1(client.encode('utf-8')).digest()[:4]
    query_hash = hashlib.sha1(query.encode('utf-8')).digest()[:4]
    payload = version_b + ts_b + result_b + click_b + client_hash + query_hash
    checksum = struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    secret = hashlib.sha256(b"ved-secret-salt").digest()[:8]
    sig = hashlib.sha256(payload + secret).digest()[:8]
    full = payload + checksum + sig
    ved = base64.urlsafe_b64encode(full).decode('ascii').rstrip('=')
    return ved

def make_gs_lp(query):
    payload = f"gws-wiz-serp|q={query}|ts={int(time.time())}|r={random.randint(0,9999)}"
    raw = payload.encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')

def build_google_search_url(query,
                            client='firefox-b-d',
                            include_tracking=True,
                            lang=None,
                            gl=None,
                            start=None,
                            num=None,
                            result_index=0,
                            click_type=0):
    base = "https://www.google.com/search"
    q_enc = quote_plus(query, safe='')
    params = [f"q={q_enc}", f"oq={q_enc}", f"client={quote_plus(client)}"]
    if lang:
        params.append(f"hl={quote_plus(lang)}")
    if gl:
        params.append(f"gl={quote_plus(gl)}")
    if start is not None:
        params.append(f"start={int(start)}")
    if num is not None:
        params.append(f"num={int(num)}")
    if include_tracking:
        params.append(f"sca_esv={random_hex(32)}")
        params.append(f"ei={make_ei(query)}")
        params.append(f"ved={make_ved_plausible(query, result_index=result_index, click_type=click_type, client=client)}")
        params.append(f"uact={random.randint(1,7)}")
        params.append(f"gs_lp={make_gs_lp(query)}")
        params.append("sclient=gws-wiz-serp")
    query_string = "&".join(params)
    return f"{base}?{query_string}"

def parse_proxy_table(text: str, threshold_ms: int = 1000) -> List[str]:
    """
    Parse un tableau texte contenant des colonnes (IP address, Port, ..., Speed, Type, ...)
    et retourne une liste de proxies sous forme d'URL utilisable par Chrome:
      - http proxies -> "http://IP:PORT"
      - socks proxies -> "socks5://IP:PORT" ou "socks4://IP:PORT" selon Type trouvé
    Filtre sur la colonne Speed en ms (garde les entrées <= threshold_ms).
    """
    proxies = []
    # lignes possibles séparées par retours ligne
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # tenter d'extraire IP et port en début de ligne
        m = re.match(r"^(\d{1,3}(?:\.\d{1,3}){3})\s+(\d+)\s+.*?(\d+)\s*ms.*\b(SOCKS5|SOCKS4|SOCKS|HTTP)\b", line, re.IGNORECASE)
        if not m:
            # essai alternatif: IP, Port puis Speed mais sans Type
            m2 = re.match(r"^(\d{1,3}(?:\.\d{1,3}){3})\s+(\d+).*?(\d+)\s*ms", line)
            if m2:
                ip, port, speed = m2.group(1), m2.group(2), int(m2.group(3))
                ptype = "HTTP"
            else:
                continue
        else:
            ip, port, speed, ptype = m.group(1), m.group(2), int(m.group(3)), m.group(4).upper()

        if speed > threshold_ms:
            continue

        if "SOCKS5" in ptype or "SOCKS" in ptype and "5" in ptype:
            proxy_url = f"socks5://{ip}:{port}"
        elif "SOCKS4" in ptype:
            proxy_url = f"socks4://{ip}:{port}"
        else:
            proxy_url = f"http://{ip}:{port}"

        proxies.append(proxy_url)

    # dédupliquer tout en gardant l'ordre
    seen = set()
    res = []
    for p in proxies:
        if p not in seen:
            seen.add(p)
            res.append(p)
    return res


# pool d'user-agents variée — 30+ user agents
DEFAULT_USER_AGENT_POOL = [
    # Chrome Windows Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    # Firefox Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
    # Mobile Chrome / Safari
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) OPR/100.0.0.0 Chrome/119.0.0.0 Safari/537.36",
    # Android Firefox
    "Mozilla/5.0 (Android 14; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
    # divers (travail de camouflage)
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    # ajouter autant que souhaité...
]