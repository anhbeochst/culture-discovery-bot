import requests
import json

GENIUS_API = "https://api.genius.com"


def search_song(access_token, query, limit=3):
    if not access_token:
        return [], 0
    url = f"{GENIUS_API}/search?q={requests.utils.quote(query)}"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    if not resp.ok:
        return [], 0
    data = resp.json()
    hits = (data.get("response", {}).get("hits", []) or [])[:limit]
    results = []
    for hit in hits:
        result = hit.get("result", {})
        results.append({
            "title": result.get("title", ""),
            "artist": result.get("primary_artist", {}).get("name", ""),
            "url": result.get("url", ""),
            "image": result.get("song_art_image_thumbnail_url", ""),
            "release_date": result.get("release_date_for_display", ""),
        })
    return results, len(hits)
