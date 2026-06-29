import requests
from datetime import datetime


def send_report(
    webhook_url, culture_data, folkways, instruments, artists, artworks, songs
):
    today = datetime.now().strftime("%d/%m/%Y")
    culture_name = culture_data["name"]
    country = culture_data["country"]
    region = culture_data["region"]

    embeds = []

    embeds.append(
        {
            "title": f"🌍 {culture_name} — Khám phá văn hóa hôm nay",
            "color": 0x2ECC71,
            "description": (
                f"**Quốc gia:** {country}  ·  **Khu vực:** {region}\n\n"
                f"Mỗi ngày một nền văn hóa — âm nhạc, nghệ thuật và di sản từ khắp thế giới."
            ),
            "footer": {"text": f"Culture Discovery Bot — {today}"},
        }
    )

    smithsonian_embed = _build_folkways_embed(folkways, culture_name, today)
    if smithsonian_embed:
        embeds.append(smithsonian_embed)

    mb_embed = _build_musicbrainz_embed(instruments, artists, culture_name, today)
    if mb_embed:
        embeds.append(mb_embed)

    met_embed = _build_met_embed(artworks, culture_name, today)
    if met_embed:
        embeds.append(met_embed)

    songs_embed = _build_genius_embed(songs, culture_name, today)
    if songs_embed:
        embeds.append(songs_embed)

    payload = {"embeds": embeds}
    resp = requests.post(webhook_url, json=payload, timeout=15)
    resp.raise_for_status()
    return True


def _truncate(text, maxlen=1000):
    if not text:
        return ""
    text = str(text)
    if len(text) > maxlen:
        return text[: maxlen - 3] + "..."
    return text


def _build_folkways_embed(folkways, culture_name, today):
    if not folkways:
        return None
    fw = folkways[0]
    fields = []
    fields.append(
        {
            "name": "📀 Tiêu đề",
            "value": _truncate(fw.get("title", "—"), 240),
            "inline": False,
        }
    )
    if fw.get("culture"):
        fields.append({"name": "Văn hóa", "value": fw["culture"], "inline": True})
    if fw.get("topic"):
        fields.append(
            {"name": "Chủ đề", "value": _truncate(fw["topic"], 240), "inline": True}
        )
    if fw.get("description"):
        fields.append(
            {"name": "Mô tả", "value": _truncate(fw["description"]), "inline": False}
        )

    extra = []
    if fw.get("media_url"):
        extra.append(f"[🎵 Nghe thử]({fw['media_url']})")
    if fw.get("record_url"):
        extra.append(f"[📖 Xem chi tiết]({fw['record_url']})")
    desc = _truncate(fw.get("description", ""), 500)
    return {
        "title": f"🎵 Smithsonian Folkways — {culture_name}",
        "color": 0xE67E22,
        "description": f"Bản ghi âm thực địa từ kho tàng Folkways của Smithsonian:\n\n{desc}\n\n{'  ·  '.join(extra) if extra else ''}"
        if desc
        else f"{'  ·  '.join(extra) if extra else ''}",
        "fields": fields,
        "footer": {"text": f"Smithsonian Open Access — {today}"},
    }


def _build_musicbrainz_embed(instruments, artists, culture_name, today):
    fields = []
    if instruments:
        inst_lines = []
        for inst in instruments[:5]:
            line = f"**{inst['name']}**"
            if inst.get("description"):
                line += f" — {_truncate(inst['description'], 100)}"
            inst_lines.append(line)
        fields.append(
            {
                "name": f"🎸 Nhạc cụ truyền thống ({len(instruments)} tìm thấy)",
                "value": "\n".join(inst_lines[:5])
                if inst_lines
                else "Không có dữ liệu",
                "inline": False,
            }
        )

    if artists:
        art_lines = []
        for a in artists[:3]:
            line = f"**{a['name']}** ({a.get('type', '?')})"
            if a.get("begin"):
                line += f" — thành lập {a['begin']}"
            art_lines.append(line)
        fields.append(
            {
                "name": f"🎤 Nghệ sĩ tiêu biểu",
                "value": "\n".join(art_lines) if art_lines else "Không có dữ liệu",
                "inline": False,
            }
        )

    if not fields:
        return None
    return {
        "title": f"🎼 MusicBrainz — {culture_name}",
        "color": 0x3498DB,
        "fields": fields,
        "footer": {"text": f"MusicBrainz — {today}"},
    }


def _build_met_embed(artworks, culture_name, today):
    if not artworks:
        return None
    art = artworks[0]
    fields = []
    fields.append(
        {
            "name": "🖼 Tác phẩm",
            "value": _truncate(art.get("title", "—"), 240),
            "inline": False,
        }
    )
    if art.get("artist"):
        fields.append(
            {"name": "Tác giả", "value": _truncate(art["artist"], 240), "inline": True}
        )
    if art.get("date"):
        fields.append({"name": "Niên đại", "value": art["date"], "inline": True})
    if art.get("medium"):
        fields.append(
            {
                "name": "Chất liệu",
                "value": _truncate(art["medium"], 240),
                "inline": False,
            }
        )
    if art.get("department"):
        fields.append(
            {"name": "Phòng trưng bày", "value": art["department"], "inline": True}
        )

    embed = {
        "title": f"🎨 {art.get('title', 'Tác phẩm nghệ thuật')}",
        "color": 0x9B59B6,
        "fields": fields,
        "url": art.get("url", ""),
        "footer": {"text": f"Art Institute of Chicago — {today}"},
    }
    if art.get("image"):
        embed["image"] = {"url": art["image"]}
    return embed


def _build_genius_embed(songs, culture_name, today):
    if not songs:
        return None
    song = songs[0]
    fields = []
    fields.append(
        {"name": "🎤 Bài hát", "value": song.get("title", "—"), "inline": False}
    )
    fields.append({"name": "Nghệ sĩ", "value": song.get("artist", "—"), "inline": True})
    if song.get("release_date"):
        fields.append(
            {"name": "Phát hành", "value": song["release_date"], "inline": True}
        )

    return {
        "title": f"📝 Genius — {song.get('title', 'Bài hát')}",
        "color": 0xFFFF00,
        "url": song.get("url", ""),
        "fields": fields,
        "thumbnail": {"url": song.get("image", "")} if song.get("image") else None,
        "footer": {"text": f"Genius — {today}"},
    }
