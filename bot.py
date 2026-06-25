import os
import sys
import random
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.cultures import CULTURES
from src.smithsonian import search_folkways
from src.musicbrainz import get_folk_instruments, search_artist, search_recording_by_country
from src.met_museum import search_art
from src.genius import search_song
from src.discord_embed import send_report

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def main():
    smithsonian_key = os.environ.get("SMITHSONIAN_API_KEY") or "DEMO_KEY"
    genius_token = os.environ.get("GENIUS_ACCESS_TOKEN", "")
    webhook = os.environ.get(
        "DISCORD_WEBHOOK_URL",
        os.environ.get("DISCORD_WEBHOOK_LUNAR", ""),
    )
    if not webhook:
        log.error("DISCORD_WEBHOOK_URL not set")
        sys.exit(1)

    seed = int(datetime.now().strftime("%Y%m%d"))
    rng = random.Random(seed)
    culture = rng.choice(CULTURES)
    log.info("Today: %s (%s)", culture["name"], culture["country"])

    log.info("[1/5] Searching Smithsonian Folkways...")
    folkways = []
    try:
        folkways = search_folkways(smithsonian_key, culture["search_terms"])
        log.info("  → %d Folkways results", len(folkways))
    except Exception as e:
        log.warning("  Smithsonian error: %s", e)

    log.info("[2/5] Querying MusicBrainz...")
    instruments = []
    artists = []
    try:
        instruments = get_folk_instruments(culture["country"])
        artists = search_artist(culture["mb_country"])
        log.info("  → %d instruments, %d artists", len(instruments), len(artists))
    except Exception as e:
        log.warning("  MusicBrainz error: %s", e)

    log.info("[3/5] Fetching Met Museum artwork...")
    artworks, art_total = [], 0
    try:
        for term in culture["search_terms"]:
            artworks, art_total = search_art(term)
            if artworks:
                break
        if not artworks:
            artworks, art_total = search_art(culture["region"])
        log.info("  → %d artworks found (total %d)", len(artworks), art_total)
    except Exception as e:
        log.warning("  Met Museum error: %s", e)

    log.info("[4/5] Searching Genius...")
    songs = []
    if genius_token:
        try:
            songs, _ = search_song(genius_token, f"{culture['country']} folk music")
            log.info("  → %d Genius results", len(songs))
        except Exception as e:
            log.warning("  Genius error: %s", e)
    else:
        log.info("  → Genius token not set, skipping")

    log.info("[5/5] Sending Discord report...")
    try:
        send_report(webhook, culture, folkways, instruments, artists, artworks, songs)
        log.info("  ✓ Report sent successfully!")
    except Exception as e:
        log.error("  Discord error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
