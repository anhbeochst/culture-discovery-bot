import requests
import time

BASE = "https://api.si.edu/openaccess/api/v1.0"


def _fetch(q, api_key, rows=5):
    url = f"{BASE}/search"
    params = {"q": q, "api_key": api_key, "rows": rows, "start": 0}
    resp = requests.get(url, params=params, timeout=15)
    if resp.status_code == 429:
        return None
    resp.raise_for_status()
    return resp.json()


def _parse_row(r):
    title = r.get("title", "").replace(" [sound recording]", "").strip()
    unit = r.get("unitCode", "")
    if "FOLKLIFE" not in (unit or ""):
        return None

    content = r.get("content", {})
    dnr = content.get("descriptiveNonRepeating", {})
    media_list = dnr.get("online_media", {}).get("media", [])
    thumbnail = media_list[0].get("thumbnail", "") if media_list else ""
    media_url = media_list[0].get("content", "") if media_list else ""

    freetext = r.get("freetext", {})
    culture = (freetext.get("culture") or [{}])[0].get("content", "") if freetext.get("culture") else ""
    topic = (freetext.get("topic") or [{}])[0].get("content", "") if freetext.get("topic") else ""

    desc_blocks = dnr.get("notes", [])
    description = ""
    for b in desc_blocks:
        if isinstance(b, dict):
            description += b.get("content", "") + "\n"

    record_url = ""
    if isinstance(content, dict):
        for key, val in content.items():
            if isinstance(val, dict) and val.get("url"):
                record_url = val["url"]
                break

    return {
        "title": title,
        "culture": culture,
        "topic": topic,
        "description": description.strip()[:500],
        "thumbnail": thumbnail,
        "media_url": media_url,
        "record_url": record_url,
        "unit": unit,
    }


def search_folkways(api_key, search_terms, rows=5):
    for term in search_terms:
        q = f'folkways "{term}" music'
        data = _fetch(q, api_key, rows)
        if data is None:
            time.sleep(1)
            data = _fetch(q, api_key, rows)
        if data is None:
            continue
        results = []
        for r in (data.get("response", {}).get("rows", []) or []):
            parsed = _parse_row(r)
            if parsed:
                results.append(parsed)
        if results:
            return results

        q2 = f'folkways "{term}"'
        data = _fetch(q2, api_key, rows)
        if data is None:
            continue
        results = []
        for r in (data.get("response", {}).get("rows", []) or []):
            parsed = _parse_row(r)
            if parsed:
                results.append(parsed)
        if results:
            return results

    return []
