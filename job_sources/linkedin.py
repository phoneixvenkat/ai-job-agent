import requests
import urllib3
from bs4 import BeautifulSoup
from backend.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = get_logger("linkedin")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# LinkedIn frequently changes class names; try multiple selector sets
_CARD_SELECTORS    = [".job-search-card", ".base-card", "[data-entity-urn]"]
_TITLE_SELECTORS   = [".base-search-card__title", "h3.base-search-card__title", "h3"]
_COMPANY_SELECTORS = [".base-search-card__subtitle", "h4.base-search-card__subtitle", "h4"]
_LOC_SELECTORS     = [".job-search-card__location", ".base-search-card__metadata", "span.job-search-card__location"]
_LINK_SELECTORS    = ["a.base-card__full-link", "a[href*='/jobs/view/']", "a[data-tracking-id]"]


def _try_select(el, selectors):
    for sel in selectors:
        found = el.select_one(sel)
        if found:
            return found
    return None


def fetch_linkedin(role: str, location: str = "remote", limit: int = 20) -> list:
    url = (
        f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={role.replace(' ', '%20')}&location={location}"
        f"&f_TPR=r86400&sortBy=DD&start=0"
    )
    try:
        r = requests.get(url, headers=_HEADERS, timeout=20, verify=False)
        if r.status_code in (429, 999):
            log.warning("LinkedIn rate-limited (status %d) for '%s'", r.status_code, role)
            return []
        if r.status_code != 200:
            log.warning("LinkedIn status %d for '%s'", r.status_code, role)
            return []

        soup  = BeautifulSoup(r.text, "html.parser")
        cards = []
        for sel in _CARD_SELECTORS:
            cards = soup.select(sel)
            if cards:
                break

        jobs = []
        for card in cards[:limit]:
            title_el   = _try_select(card, _TITLE_SELECTORS)
            company_el = _try_select(card, _COMPANY_SELECTORS)
            loc_el     = _try_select(card, _LOC_SELECTORS)
            link_el    = _try_select(card, _LINK_SELECTORS)
            date_el    = card.select_one("time")
            if not title_el:
                continue
            href = ""
            if link_el:
                href = link_el.get("href", "")
                if href and "?" in href:
                    href = href.split("?")[0]
            jobs.append({
                "source":    "LinkedIn",
                "org":       company_el.get_text(strip=True) if company_el else "",
                "title":     title_el.get_text(strip=True),
                "location":  loc_el.get_text(strip=True) if loc_el else location,
                "url":       href,
                "dept":      "",
                "posted_at": date_el.get("datetime", "") if date_el else "",
                "description": "",
            })

        log.info("LinkedIn '%s': %d jobs", role, len(jobs))
        return jobs
    except Exception as e:
        log.warning("LinkedIn '%s' error: %s", role, e)
        return []
