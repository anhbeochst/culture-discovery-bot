import requests
import urllib.parse
import json

BASE = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": "CultureDiscoveryBot/1.0 (github.com/anhbeochst/culture-discovery-bot)"}


def search_instruments(query, limit=5):
    url = f"{BASE}/instrument?query={urllib.parse.quote(query)}&fmt=json&limit={limit}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for inst in data.get("instruments", []):
        results.append({
            "name": inst.get("name", ""),
            "description": (inst.get("description") or "")[:200],
            "type": inst.get("type", ""),
        })
    return results


def get_folk_instruments(culture):
    mb_instruments = search_instruments(culture)
    seen = set()
    unique = []
    for i in mb_instruments:
        if i["name"].lower() not in seen:
            seen.add(i["name"].lower())
            unique.append(i)
    return unique


def search_artist(country_code, limit=5):
    url = f"{BASE}/artist?query=country:{country_code}&fmt=json&limit={limit}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for a in data.get("artists", []):
        results.append({
            "name": a.get("name", ""),
            "type": a.get("type", ""),
            "disambiguation": (a.get("disambiguation") or "")[:120],
            "begin": (a.get("life-span") or {}).get("begin", ""),
        })
    return results


def search_recording_by_country(country_code, limit=3):
    url = f"{BASE}/recording?query=country:{country_code}&fmt=json&limit={limit}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for r in data.get("recordings", []):
        ac = r.get("artist-credit") or []
        artist_name = ac[0].get("name", "") if ac else ""
        results.append({
            "title": r.get("title", ""),
            "artist": artist_name,
            "length": r.get("length"),
        })
    return results
