import os
import sys
import random
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cultures import CULTURES
from src.smithsonian import search_folkways
from src.musicbrainz import get_folk_instruments, search_artist
from src.art import search_art
from src.genius import search_song
from src.discord_embed import send_report

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def find_culture(query):
    query_lower = query.lower().strip()
    for c in CULTURES:
        if (
            query_lower == c["slug"]
            or query_lower == c["country"].lower()
            or query_lower == c["name"].lower()
        ):
            return c
    for c in CULTURES:
        if query_lower in c["country"].lower() or query_lower in c["name"].lower():
            return c
    return None


def search(culture, smithsonian_key, genius_token):
    log.info("[1/4] Smithsonian Folkways...")
    folkways = []
    try:
        folkways = search_folkways(smithsonian_key, culture["search_terms"])
        log.info("  → %d kết quả", len(folkways))
    except Exception as e:
        log.warning("  Smithsonian error: %s", e)

    log.info("[2/4] MusicBrainz...")
    instruments = []
    artists = []
    try:
        instruments = get_folk_instruments(culture["country"])
        artists = search_artist(culture["mb_country"])
        log.info("  → %d nhạc cụ, %d nghệ sĩ", len(instruments), len(artists))
    except Exception as e:
        log.warning("  MusicBrainz error: %s", e)

    log.info("[3/4] Art Institute of Chicago...")
    artworks, art_total = [], 0
    try:
        keywords = culture["search_terms"] + [culture["country"]]
        artworks, art_total = search_art(culture["country"], keywords=keywords)
        log.info("  → %d tác phẩm KHỚP văn hóa (tổng tìm %d)", len(artworks), art_total)
    except Exception as e:
        log.warning("  Art error: %s", e)

    log.info("[4/4] Genius...")
    songs = []
    if genius_token:
        try:
            songs, _ = search_song(genius_token, f"{culture['country']} folk music")
            log.info("  → %d kết quả", len(songs))
        except Exception as e:
            log.warning("  Genius error: %s", e)
    else:
        log.info("  → Bỏ qua (không có token)")

    return folkways, instruments, artists, artworks, songs


def print_report(culture, folkways, instruments, artists, artworks, songs):
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  🌍  {culture['name']}  —  {culture['country']} ({culture['region']})")
    print(f"{sep}\n")

    if folkways:
        fw = folkways[0]
        print(f"  🎵  Smithsonian Folkways")
        print(f"      {fw['title']}")
        if fw.get("description"):
            print(f"      {fw['description'][:200]}")
        print()
    else:
        print(f"  🎵  Smithsonian Folkways: không có dữ liệu\n")

    if instruments:
        print(f"  🎸  Nhạc cụ truyền thống ({len(instruments)}):")
        for inst in instruments[:5]:
            print(f"      • {inst['name']}")
        print()

    if artists:
        print(f"  🎤  Nghệ sĩ ({len(artists)}):")
        for a in artists[:3]:
            print(f"      • {a['name']} ({a.get('type', '?')})")
        print()

    if artworks:
        art = artworks[0]
        print(f"  🎨  Art (AIC): {art['title']}")
        print(f"      Tác giả: {art['artist']}  ·  {art['date']}")
        if art.get("image"):
            print(f"      Ảnh: {art['image']}")
        print()

    if songs:
        s = songs[0]
        print(f"  📝  Genius: {s['title']} — {s['artist']}")
        print(f"      {s['url']}")
        print()

    print(f"{sep}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Culture Discovery Bot — 4 API kết hợp"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "country",
        nargs="?",
        default=None,
        help="Tên quốc gia hoặc văn hóa (vd: vietnam, japan, india)",
    )
    group.add_argument(
        "--random", "-r", action="store_true", help="Chọn ngẫu nhiên một nền văn hóa"
    )
    group.add_argument(
        "--list", "-l", action="store_true", help="Danh sách các nền văn hóa có sẵn"
    )
    parser.add_argument(
        "--print", "-p", action="store_true", help="In ra terminal thay vì gửi Discord"
    )

    args = parser.parse_args()

    if args.list:
        print(f"\n{'=' * 50}")
        print(f"  🌍  Danh sách nền văn hóa ({len(CULTURES)})")
        print(f"{'=' * 50}")
        for c in CULTURES:
            print(f"  • {c['name']:12s}  — {c['country']:15s} ({c['region']})")
        print(f"{'=' * 50}")
        print(f"  Gõ: python bot.py <tên>  (vd: python bot.py vietnam)")
        print()
        return

    smithsonian_key = os.environ.get("SMITHSONIAN_API_KEY") or "DEMO_KEY"
    genius_token = os.environ.get("GENIUS_ACCESS_TOKEN", "")
    webhook = os.environ.get(
        "DISCORD_WEBHOOK_URL", os.environ.get("DISCORD_WEBHOOK_LUNAR", "")
    )

    if args.country:
        culture = find_culture(args.country)
        if not culture:
            print(f"Không tìm thấy '{args.country}'")
            print(f"Xem danh sách: python bot.py --list")
            sys.exit(1)
    else:
        seed = int(datetime.now().strftime("%Y%m%d"))
        rng = random.Random(seed)
        culture = rng.choice(CULTURES)

    log.info("🌍  %s (%s)", culture["name"], culture["country"])
    folkways, instruments, artists, artworks, songs = search(
        culture, smithsonian_key, genius_token
    )

    if args.print or not webhook:
        print_report(culture, folkways, instruments, artists, artworks, songs)
    else:
        log.info("Gửi Discord...")
        try:
            send_report(
                webhook, culture, folkways, instruments, artists, artworks, songs
            )
            log.info("✓ Đã gửi thành công!")
        except Exception as e:
            log.error("Discord error: %s", e)
            sys.exit(1)


if __name__ == "__main__":
    main()
