import requests
import json

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"


def search_art(query, limit=3):
    url = f"{BASE}/search?q={requests.utils.quote(query)}&hasImages=true"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    total = data.get("total", 0)
    object_ids = (data.get("objectIDs") or [])[:limit]

    results = []
    for oid in object_ids:
        obj_url = f"{BASE}/objects/{oid}"
        obj_resp = requests.get(obj_url, timeout=10)
        if not obj_resp.ok:
            continue
        obj = obj_resp.json()

        results.append({
            "title": obj.get("title", ""),
            "artist": obj.get("artistDisplayName") or obj.get("culture") or "",
            "date": obj.get("objectDate", ""),
            "medium": obj.get("medium", "")[:120],
            "image": obj.get("primaryImage", "") or obj.get("primaryImageSmall", ""),
            "image_small": obj.get("primaryImageSmall", ""),
            "url": obj.get("objectURL", ""),
            "department": obj.get("department", ""),
        })

    return results, total
