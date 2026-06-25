#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -d venv ]; then
    source venv/bin/activate
fi

python3 -c "import py_compile; py_compile.compile('bot.py', doraise=True)"
python3 -c "
import py_compile, glob
for f in glob.glob('src/*.py'):
    py_compile.compile(f, doraise=True)
"
echo '✓ verify.sh: syntax OK'

python3 << 'PYEOF'
from src.cultures import CULTURES
assert len(CULTURES) >= 15, f"Expected >=15 cultures, got {len(CULTURES)}"

from src.smithsonian import search_folkways
results = search_folkways("DEMO_KEY", ["vietnam", "Vietnamese"])
assert isinstance(results, list)
print(f"✓ Smithsonian API works ({len(results)} results)")

from src.musicbrainz import get_folk_instruments, search_artist
insts = get_folk_instruments("Vietnam")
assert isinstance(insts, list)
artists = search_artist("VN")
assert isinstance(artists, list)
print(f"✓ MusicBrainz API works ({len(insts)} instruments, {len(artists)} artists)")

from src.met_museum import search_art
artworks, total = search_art("vietnam")
assert isinstance(artworks, list)
print(f"✓ Met Museum API works ({len(artworks)} artworks of {total})")

print("✓ All checks passed")
PYEOF
