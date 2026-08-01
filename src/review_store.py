from __future__ import annotations
from datetime import datetime
from typing import Iterable
import os
import streamlit as st
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    insert,
    select,
)
from sqlalchemy.engine import Engine
from src.settings import get_settings

metadata = MetaData()

reviews_table = Table(
    'reviews',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column('name', String(120), nullable=False),
    Column('role', String(120), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('model_used', String(60), nullable=False),
    Column('comment', Text, nullable=False),
    Column('user_hash', String(120), nullable=True),
    CheckConstraint('rating >= 1 AND rating <= 5', name='reviews_rating_between_1_and_5'),
)

prediction_logs_table = Table(
    'prediction_logs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column('model_used', String(60), nullable=False),
    Column('source', String(40), nullable=False),
    Column('user_hash', String(120), nullable=True),
    Column('horizon_days', Integer, nullable=False),
    Column('predicted_used_gb', String(32), nullable=False),
    Column('predicted_used_pct', String(32), nullable=False),
)

_engine: Engine | None = None


def _safe_secret_get(key: str, default=None):
    """Read st.secrets safely without crashing when secrets.toml is missing."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def _resolve_database_url() -> str:
    # 1) Azure App Setting (recommended in production)
    db_url = os.getenv("DATABASE_URL")

    # 2) Streamlit secrets top-level key
    if not db_url:
        db_url = _safe_secret_get("DATABASE_URL", None)

    # 3) Streamlit nested key: [database] url = "..."
    if not db_url:
        db_cfg = _safe_secret_get("database", {})
        if isinstance(db_cfg, dict):
            db_url = db_cfg.get("url")

    # 4) Local settings fallback
    if not db_url:
        db_url = get_settings().database_url

    # 5) Final safety fallback
    if not db_url:
        db_url = "sqlite:///reviews.db"

    return db_url


def _normalize_db_url(db_url: str) -> str:
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+psycopg://", 1)
    if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        return db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return db_url


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        db_url = _normalize_db_url(_resolve_database_url())
        connect_args = {'check_same_thread': False} if db_url.startswith('sqlite') else {}
        _engine = create_engine(
            db_url,
            future=True,
            pool_pre_ping=True,
            connect_args=connect_args
        )
    return _engine


def init_store() -> None:
    metadata.create_all(get_engine())


def backend_label() -> str:
    engine = get_engine()
    url_str = str(engine.url)
    if "postgresql" in url_str:
        return 'PostgreSQL (managed)'
    if "sqlite" in url_str:
        return 'SQLite (local fallback)'
    return url_str.split(':', 1)[0]


def healthcheck() -> dict:
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(select(1))
        return {'ok': True, 'backend': backend_label()}
    except Exception as exc:
        return {'ok': False, 'backend': backend_label(), 'error': str(exc)}


def save_review(name: str, role: str, rating: int, model_used: str, comment: str, user_hash: str | None = None) -> None:
    init_store()
    payload = {
        'name': (name or 'Anonymous').strip()[:120],
        'role': (role or 'Unknown').strip()[:120],
        'rating': int(rating),
        'model_used': model_used.strip()[:60],
        'comment': comment.strip()[:4000],
        'user_hash': (user_hash or '').strip()[:120] or None,
    }
    with get_engine().begin() as conn:
        conn.execute(insert(reviews_table).values(**payload))


def load_reviews(limit: int = 100) -> list[dict]:
    init_store()
    stmt = select(
        reviews_table.c.created_at,
        reviews_table.c.name,
        reviews_table.c.role,
        reviews_table.c.rating,
        reviews_table.c.model_used,
        reviews_table.c.comment,
    ).order_by(reviews_table.c.id.desc()).limit(limit)
    with get_engine().connect() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [dict(r) for r in rows]


def log_predictions(model_used: str, source: str, rows: Iterable[dict], user_hash: str | None = None) -> None:
    init_store()
    payload = []
    for row in rows:
        payload.append({
            'model_used': model_used[:60],
            'source': source[:40],
            'user_hash': (user_hash or '').strip()[:120] or None,
            'horizon_days': int(row['horizon_days']),
            'predicted_used_gb': str(row['predicted_used_gb']),
            'predicted_used_pct': str(row['predicted_used_pct']),
        })
    if not payload:
        return
    with get_engine().begin() as conn:
        conn.execute(insert(prediction_logs_table), payload)


def review_summary() -> dict:
    init_store()
    with get_engine().connect() as conn:
        total = conn.execute(select(func.count()).select_from(reviews_table)).scalar_one()
        avg_rating = conn.execute(select(func.avg(reviews_table.c.rating))).scalar()
        total_predictions = conn.execute(select(func.count()).select_from(prediction_logs_table)).scalar_one()
    return {
        'total_reviews': int(total),
        'avg_rating': float(avg_rating) if avg_rating is not None else None,
        'total_predictions_logged': int(total_predictions),
        'backend': backend_label(),
        'checked_at': datetime.utcnow().isoformat() + 'Z',
    }