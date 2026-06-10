from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database_url: str
    environment: str
    app_base_url: str
    model_registry_dir: Path
    review_export_dir: Path



def get_settings() -> Settings:
    default_sqlite = f"sqlite:///{(ROOT / 'data' / 'app_reviews.db').as_posix()}"
    database_url = os.getenv('DATABASE_URL', default_sqlite)
    environment = os.getenv('APP_ENV', 'development')
    app_base_url = os.getenv('APP_BASE_URL', 'http://localhost:8501')
    model_registry_dir = ROOT / 'models'
    review_export_dir = ROOT / 'reports'
    return Settings(
        database_url=database_url,
        environment=environment,
        app_base_url=app_base_url,
        model_registry_dir=model_registry_dir,
        review_export_dir=review_export_dir,
    )
