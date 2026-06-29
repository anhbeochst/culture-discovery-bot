"""Nghệ thuật theo văn hóa qua Art Institute of Chicago (API công khai, KHÔNG key).

Lọc theo place_of_origin/tiêu đề để CHỈ lấy tác phẩm khớp văn hóa — tránh bug
"đồ Ai Cập cho Việt Nam" của Met Museum (collection Met nghèo đồ Á/folk, search
full-text không lọc văn hóa).
"""

import requests

SEARCH = "https://api.artic.edu/api/v1/artworks/search"
IIIF = "https://www.artic.edu/iiif/2/{img}/full/843,/0/default.jpg"
PAGE = "https://www.artic.edu/artworks/{id}"
HEADERS = {
    "User-Agent": "CultureDiscoveryBot/1.0 (github.com/anhbeochst/culture-discovery-bot)"
}
FIELDS = "id,title,artist_display,place_of_origin,date_display,medium_display,image_id,department_title"


def search_art(query, keywords=None, limit=12):
    """Trả (results, total). results CHỈ gồm tác phẩm khớp keyword văn hóa."""
    params = {"q": query, "fields": FIELDS, "limit": limit}
    resp = requests.get(SEARCH, params=params, headers=HEADERS, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    total = (data.get("pagination") or {}).get("total", 0)
    kws = [k.lower() for k in (keywords or [query])]

    def _item(a):
        img = a.get("image_id")
        return {
            "title": a.get("title", ""),
            "artist": a.get("artist_display") or a.get("place_of_origin") or "",
            "date": a.get("date_display", ""),
            "medium": (a.get("medium_display") or "")[:120],
            "image": IIIF.format(img=img) if img else "",
            "url": PAGE.format(id=a.get("id", "")),
            "department": a.get("department_title", ""),
        }

    # Ưu tiên tác phẩm có XUẤT XỨ khớp văn hóa (đồ thật của nền đó); chỉ khi
    # không có mới lấy theo tiêu đề (tránh vớ ảnh "chiến tranh VN" của tác giả Mỹ).
    place_hits, title_hits = [], []
    for a in data.get("data", []):
        place = (a.get("place_of_origin") or "").lower()
        title = (a.get("title") or "").lower()
        if any(k in place for k in kws):
            place_hits.append(_item(a))
        elif any(k in title for k in kws):
            title_hits.append(_item(a))
    return (place_hits or title_hits)[:3], total
