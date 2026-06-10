from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.review_store import load_reviews

OUT_PATH = ROOT / 'reports' / 'reviews_export.csv'


if __name__ == '__main__':
    rows = load_reviews(limit=100000)
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False)
    print(f'Exported {len(rows)} reviews to {OUT_PATH}')
