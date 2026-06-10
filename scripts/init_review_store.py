from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.review_store import healthcheck, init_store, review_summary


if __name__ == '__main__':
    init_store()
    print('Review store initialized')
    print(healthcheck())
    print(review_summary())
