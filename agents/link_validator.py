import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.state import LeadGenState, RawLead

TIMEOUT = 6
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeadBot/1.0)"}


def _check(lead: RawLead) -> tuple[RawLead, bool]:
    url = lead["url"]
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT, headers=HEADERS)
        if r.status_code == 405:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT, headers=HEADERS)
        alive = r.status_code < 400 or r.status_code == 403
    except Exception:
        alive = False
    status = "✓" if alive else "✗"
    print(f"  {status} {url[:60]}")
    return lead, alive


def validate_links(state: LeadGenState) -> LeadGenState:
    print("[2/5] 🔗 Validating links...")
    leads = state["raw_leads"]

    valid: list[RawLead] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_check, lead): lead for lead in leads}
        for future in as_completed(futures):
            lead, alive = future.result()
            if alive:
                valid.append(lead)

    valid.sort(key=lambda l: leads.index(l))
    print(f"  {len(valid)}/{len(leads)} links are live")
    return {**state, "raw_leads": valid, "status": "links_validated"}
