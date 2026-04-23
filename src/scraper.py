"""
scraper.py - IR Smart Match Company Data Scraper
-------------------------------------------------
Pipeline:
  1. Reads companies.json (names only, empty descriptions)
  2. For each company, scrapes a rich description from:
       a. Wikipedia API
       b. Google search snippet
       c. Company careers/about page
  3. Writes enriched descriptions back to companies.json

USAGE:
  python scraper.py                          # enrich all companies
  python scraper.py --skip-existing          # skip already-scraped ones
  python scraper.py --company "Lockheed"     # test a single company
"""

import json
import time
import re
import argparse
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run:  pip install requests beautifulsoup4")
    sys.exit(1)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

DATA_PATH = Path(__file__).parent.parent / "data" / "companies.json"
DELAY = 1.5


# Source 1: Wikipedia
def fetch_wikipedia(company_name: str) -> str | None:
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": company_name + " company",
        "format": "json",
        "srlimit": 1,
    }
    try:
        r = requests.get(search_url, params=params, headers=HEADERS, timeout=8)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        if not results:
            return None

        title = results[0]["title"]
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": title,
            "format": "json",
        }
        r2 = requests.get(search_url, params=extract_params, headers=HEADERS, timeout=8)
        r2.raise_for_status()
        pages = r2.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        extract = page.get("extract", "").strip()
        if not extract:
            return None
        first_para = extract.split("\n\n")[0]
        return first_para[:500].strip()

    except Exception as e:
        print(f"    [wikipedia] error: {e}")
        return None


# Source 2: Google snippet
def fetch_google_snippet(company_name: str) -> str | None:
    query = f"{company_name} company engineering careers"
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=3"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        kp = soup.find("div", {"data-attrid": "description"})
        if kp:
            text = kp.get_text(" ", strip=True)
            if len(text) > 60:
                return text[:400]

        for span in soup.select("div.VwiC3b, span.aCOpRe"):
            text = span.get_text(" ", strip=True)
            if len(text) > 80:
                return text[:400]

        return None
    except Exception as e:
        print(f"    [google] error: {e}")
        return None


# Source 3: Company careers/about page
def fetch_careers_page(company_name: str) -> str | None:
    slug = re.sub(r"[^a-z0-9]", "", company_name.lower().replace("&", "and"))
    candidates = [
        f"https://www.{slug}.com/careers",
        f"https://www.{slug}.com/about",
        f"https://careers.{slug}.com",
    ]
    for url in candidates:
        try:
            r = requests.get(url, headers=HEADERS, timeout=6, allow_redirects=True)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["nav", "footer", "script", "style", "header"]):
                tag.decompose()
            for p in soup.find_all("p"):
                text = p.get_text(" ", strip=True)
                if len(text) > 120:
                    return text[:450].strip()
        except Exception:
            continue
    return None


# Master fetch: tries sources in order
def get_company_description(company_name: str) -> str:
    print(f"  Scraping: {company_name}")

    desc = fetch_wikipedia(company_name)
    if desc and len(desc) > 80:
        print(f"    ✓ Wikipedia")
        return desc

    time.sleep(DELAY)
    desc = fetch_google_snippet(company_name)
    if desc and len(desc) > 80:
        print(f"    ✓ Google snippet")
        return desc

    time.sleep(DELAY)
    desc = fetch_careers_page(company_name)
    if desc and len(desc) > 80:
        print(f"    ✓ Careers page")
        return desc

    print(f"    ✗ No description found")
    return ""


def load_companies(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def save_companies(companies: list[dict], path: Path):
    with open(path, "w") as f:
        json.dump(companies, f, indent=4)
    print(f"  → Saved progress ({len(companies)} companies)")


def main():
    parser = argparse.ArgumentParser(description="IR Smart Match — Company Scraper")
    parser.add_argument("--company", metavar="NAME", help="Test a single company")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip companies that already have a description")
    parser.add_argument("--output", metavar="PATH", default=str(DATA_PATH))
    args = parser.parse_args()

    if args.company:
        desc = get_company_description(args.company)
        print(f"\nResult:\n{desc}")
        return

    out_path = Path(args.output)
    companies = load_companies(out_path)
    print(f"Loaded {len(companies)} companies from {out_path}\n")

    for company in companies:
        name = company["company"]

        if args.skip_existing and company.get("description", "").strip():
            print(f"  Skipping (exists): {name}")
            continue

        desc = get_company_description(name)
        company["description"] = desc

        # Save after every company so progress isn't lost if interrupted
        save_companies(companies, out_path)
        time.sleep(DELAY)

    print(f"\nDone! {len(companies)} companies scraped.")


if __name__ == "__main__":
    main()