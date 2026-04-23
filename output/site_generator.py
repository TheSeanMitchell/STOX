"""
output/site_generator.py — Generate static GitHub Pages site from JSON data.
"""

import os
import json
import shutil
import logging
from datetime import datetime, timezone

log = logging.getLogger("stox.sitegen")


def generate_site(data_dir: str, docs_dir: str):
    """Copy data JSON files to docs/ for GitHub Pages access."""
    os.makedirs(docs_dir, exist_ok=True)
    data_out = os.path.join(docs_dir, "data")
    os.makedirs(data_out, exist_ok=True)

    files_to_copy = [
        "signals.json",
        "articles.json",
        "trade_cards.json",
        "performance.json",
    ]

    for fname in files_to_copy:
        src = os.path.join(data_dir, fname)
        dst = os.path.join(data_out, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            log.info(f"Copied {fname} → docs/data/")
        else:
            # Write empty placeholder
            with open(dst, "w") as f:
                json.dump({"_empty": True, "generated_at": datetime.now(timezone.utc).isoformat()}, f)

    log.info("Site data updated.")
