"""
Synthetic Storage Usage Dataset Generator
==========================================
Simulates realistic daily device storage usage for multiple users
across 4 distinct behavioral profiles over a configurable period.

Key realism improvements in this version:
- profile-specific device capacity distributions
- per-user behavior parameters instead of one-size-fits-all generation
- fixed periodic cleanup scheduling for cleaner users
- pressure-driven cleanups before capacity is exceeded
- hard capacity enforcement so used_pct never becomes impossible
- output path aligned with the project structure

Output columns:
    user_id, profile, date, day_index,
    total_capacity_gb, used_gb, free_gb, used_pct,
    photos_gb, videos_gb, apps_gb, documents_gb, system_gb, other_gb,
    daily_delta_gb, cleanup_event
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ----------------------------
# Reproducibility
# ----------------------------
RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

# ----------------------------
# Config
# ----------------------------
START_DATE = datetime(2024, 1, 1)
N_DAYS = 540
USERS_PER_PROFILE = 8
OUTPUT_DIR = os.path.join("data", "synthetic")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "synthetic_storage_usage.csv")

PROFILES = ["media_heavy", "gamer", "office_user", "cleaner"]
CAPACITY_OPTIONS = [128, 256, 512, 1024]

# More realistic profile-to-device-size matching.
PROFILE_CAPACITY_PROBS = {
    "media_heavy": [0.08, 0.32, 0.45, 0.15],
    "gamer": [0.04, 0.21, 0.45, 0.30],
    "office_user": [0.30, 0.45, 0.20, 0.05],
    "cleaner": [0.18, 0.47, 0.27, 0.08],
}

REMOVABLE_KEYS = ["other", "videos", "photos", "apps", "documents"]


def sample_capacity(profile: str) -> int:
    return int(rng.choice(CAPACITY_OPTIONS, p=PROFILE_CAPACITY_PROBS[profile]))


def sample_user_config(profile: str, capacity_gb: int) -> dict:
    """Sample stable per-user behavior knobs to reduce uniformity."""
    cfg = {
        "growth_multiplier": float(rng.uniform(0.9, 1.15)),
        "cleanup_threshold_frac": float(rng.uniform(0.82, 0.92)),
        "target_utilization_after_cleanup": float(rng.uniform(0.62, 0.80)),
        "spontaneous_cleanup_prob": 0.0,
        "cleaner_interval_days": None,
        "next_cleaner_cleanup_day": None,
        "gamer_big_install_prob": None,
        "gamer_install_min_gb": None,
        "gamer_install_max_gb": None,
    }

    if profile == "media_heavy":
        cfg["spontaneous_cleanup_prob"] = float(rng.uniform(0.002, 0.008))
        cfg["cleanup_threshold_frac"] = float(rng.uniform(0.84, 0.91))
    elif profile == "gamer":
        cfg["cleanup_threshold_frac"] = float(rng.uniform(0.80, 0.88))
        cfg["target_utilization_after_cleanup"] = float(rng.uniform(0.58, 0.75))
        cfg["spontaneous_cleanup_prob"] = float(rng.uniform(0.010, 0.025))
        cfg["gamer_big_install_prob"] = float(rng.uniform(0.008, 0.018))
        cfg["gamer_install_min_gb"] = float(max(6.0, 0.04 * capacity_gb))
        cfg["gamer_install_max_gb"] = float(max(cfg["gamer_install_min_gb"] + 6.0, 0.16 * capacity_gb))
    elif profile == "office_user":
        cfg["cleanup_threshold_frac"] = float(rng.uniform(0.86, 0.94))
        cfg["target_utilization_after_cleanup"] = float(rng.uniform(0.55, 0.72))
        cfg["spontaneous_cleanup_prob"] = float(rng.uniform(0.001, 0.004))
    elif profile == "cleaner":
        cfg["cleanup_threshold_frac"] = float(rng.uniform(0.72, 0.82))
        cfg["target_utilization_after_cleanup"] = float(rng.uniform(0.45, 0.60))
        cfg["spontaneous_cleanup_prob"] = float(rng.uniform(0.015, 0.035))
        cfg["cleaner_interval_days"] = int(rng.integers(24, 36))
        cfg["next_cleaner_cleanup_day"] = int(rng.integers(20, 35))
    else:
        raise ValueError(f"Unknown profile: {profile}")

    return cfg


def base_components(capacity_gb: int, profile: str, cfg: dict) -> dict:
    """Initial GB allocation for each storage category.

    Start users in a realistic utilization band rather than near-zero or near-full.
    """
    target_used_frac = {
        "media_heavy": rng.uniform(0.18, 0.32),
        "gamer": rng.uniform(0.20, 0.35),
        "office_user": rng.uniform(0.15, 0.28),
        "cleaner": rng.uniform(0.16, 0.30),
    }[profile]

    target_used = capacity_gb * target_used_frac

    if profile == "media_heavy":
        weights = np.array([0.18, 0.16, 0.28, 0.22, 0.06, 0.10])
    elif profile == "gamer":
        weights = np.array([0.12, 0.42, 0.08, 0.06, 0.04, 0.28])
    elif profile == "office_user":
        weights = np.array([0.23, 0.16, 0.08, 0.03, 0.34, 0.16])
    else:  # cleaner
        weights = np.array([0.19, 0.18, 0.24, 0.16, 0.08, 0.15])

    jitter = rng.uniform(0.9, 1.1, size=len(weights))
    weights = weights * jitter
    weights = weights / weights.sum()

    system, apps, photos, videos, documents, other = target_used * weights

    # Keep system more stable and plausible.
    system = float(np.clip(system, 12, min(35, 0.22 * capacity_gb)))
    remaining_target = max(target_used - system, 1.0)
    variable = np.array([apps, photos, videos, documents, other])
    variable = remaining_target * (variable / variable.sum())
    apps, photos, videos, documents, other = variable

    comps = {
        "system": float(system),
        "apps": float(apps),
        "photos": float(photos),
        "videos": float(videos),
        "documents": float(documents),
        "other": float(other),
    }
    enforce_capacity(comps, capacity_gb, target_utilization=0.92)
    return comps


def daily_increment(profile: str, day_index: int, capacity_gb: int, cfg: dict) -> dict:
    """Return daily per-category growth increments in GB."""
    weekday = (START_DATE + timedelta(days=int(day_index))).weekday()
    weekend_boost = 1.0 + (0.55 if weekday >= 5 else 0.0)
    weekday_factor = 1.15 if weekday < 5 else 0.55
    season = 1.0 + 0.12 * np.sin(2 * np.pi * day_index / 365.0)
    growth = cfg["growth_multiplier"]

    if profile == "media_heavy":
        delta = {
            "photos": rng.normal(0.18, 0.05) * weekend_boost * season * growth,
            "videos": rng.normal(0.24, 0.08) * weekend_boost * season * growth,
            "apps": rng.normal(0.02, 0.01) * growth,
            "documents": rng.normal(0.01, 0.004),
            "system": rng.normal(0.003, 0.0015),
            "other": rng.normal(0.02, 0.01),
        }
    elif profile == "gamer":
        big_install = rng.random() < cfg["gamer_big_install_prob"]
        install_size = rng.uniform(cfg["gamer_install_min_gb"], cfg["gamer_install_max_gb"]) if big_install else rng.normal(0.06, 0.03)
        delta = {
            "photos": rng.normal(0.01, 0.006),
            "videos": rng.normal(0.03, 0.015) * weekend_boost,
            "apps": install_size * growth,
            "documents": rng.normal(0.004, 0.002),
            "system": rng.normal(0.004, 0.002),
            "other": rng.normal(0.03, 0.015),
        }
    elif profile == "office_user":
        delta = {
            "photos": rng.normal(0.01, 0.005),
            "videos": rng.normal(0.006, 0.003),
            "apps": rng.normal(0.015, 0.007),
            "documents": rng.normal(0.06, 0.02) * weekday_factor * growth,
            "system": rng.normal(0.003, 0.0015),
            "other": rng.normal(0.012, 0.006),
        }
    elif profile == "cleaner":
        delta = {
            "photos": rng.normal(0.12, 0.04) * weekend_boost * season * growth,
            "videos": rng.normal(0.16, 0.06) * weekend_boost * season * growth,
            "apps": rng.normal(0.02, 0.01),
            "documents": rng.normal(0.015, 0.006),
            "system": rng.normal(0.003, 0.0015),
            "other": rng.normal(0.018, 0.008),
        }
    else:
        raise ValueError(f"Unknown profile: {profile}")

    return {k: max(0.0, float(v)) for k, v in delta.items()}


def apply_cleanup(comps: dict, profile: str, intensity: str = "normal") -> dict:
    """Reduce removable categories while keeping system mostly intact."""
    if profile == "gamer":
        factors = {"apps": rng.uniform(0.68, 0.88), "photos": rng.uniform(0.88, 0.98), "videos": rng.uniform(0.80, 0.94), "documents": rng.uniform(0.95, 1.00), "other": rng.uniform(0.55, 0.80)}
    elif profile == "office_user":
        factors = {"apps": rng.uniform(0.88, 0.97), "photos": rng.uniform(0.92, 0.99), "videos": rng.uniform(0.90, 0.98), "documents": rng.uniform(0.82, 0.95), "other": rng.uniform(0.75, 0.90)}
    else:  # media_heavy / cleaner
        factors = {"apps": rng.uniform(0.90, 0.98), "photos": rng.uniform(0.72, 0.90), "videos": rng.uniform(0.55, 0.82), "documents": rng.uniform(0.92, 0.99), "other": rng.uniform(0.70, 0.88)}

    if intensity == "strong":
        factors = {k: min(v, 0.82) for k, v in factors.items()}

    for key, factor in factors.items():
        comps[key] *= factor
    return comps


def enforce_capacity(comps: dict, capacity_gb: float, target_utilization: float = 0.985) -> bool:
    """Guarantee a realistic upper bound for used storage.

    Returns True when trimming was needed.
    """
    target_used = capacity_gb * target_utilization
    total = sum(comps.values())
    if total <= target_used:
        return False

    excess = total - target_used
    for key in REMOVABLE_KEYS:
        if excess <= 1e-9:
            break
        removable = min(comps[key], excess)
        comps[key] -= removable
        excess -= removable

    # Final numerical safety net.
    total = sum(comps.values())
    if total > target_used:
        scale = target_used / total
        for key in comps:
            comps[key] *= scale
    return True


def maybe_trigger_cleanup(day_index: int, profile: str, used_frac: float, cfg: dict) -> bool:
    """Decide whether the user cleans up on this day."""
    scheduled_cleanup = False
    if profile == "cleaner" and cfg["next_cleaner_cleanup_day"] is not None and day_index >= cfg["next_cleaner_cleanup_day"]:
        scheduled_cleanup = True
        cfg["next_cleaner_cleanup_day"] += int(cfg["cleaner_interval_days"] + rng.integers(-2, 3))

    spontaneous_cleanup = rng.random() < cfg["spontaneous_cleanup_prob"]
    pressure_cleanup = used_frac >= cfg["cleanup_threshold_frac"]
    return scheduled_cleanup or spontaneous_cleanup or pressure_cleanup


def simulate_user(user_id: str, profile: str) -> list[dict]:
    capacity = sample_capacity(profile)
    cfg = sample_user_config(profile, capacity)
    comps = base_components(capacity, profile, cfg)
    records = []

    for d in range(N_DAYS):
        date = START_DATE + timedelta(days=d)
        delta = daily_increment(profile, d, capacity, cfg)

        for key, value in delta.items():
            comps[key] += value

        used_before_cleanup = sum(comps.values())
        used_frac_before_cleanup = used_before_cleanup / capacity
        cleanup = maybe_trigger_cleanup(d, profile, used_frac_before_cleanup, cfg)

        if cleanup:
            intensity = "strong" if used_frac_before_cleanup >= max(cfg["cleanup_threshold_frac"] + 0.05, 0.93) else "normal"
            comps = apply_cleanup(comps, profile, intensity=intensity)
            # Try to land near a user-specific post-cleanup target, not just barely under capacity.
            enforce_capacity(comps, capacity, target_utilization=cfg["target_utilization_after_cleanup"])

        # Hard physical constraint: never let used storage exceed device capacity.
        enforce_capacity(comps, capacity, target_utilization=0.985)

        used = sum(comps.values())
        free = capacity - used
        used_pct = 100 * used / capacity

        prev_used = records[-1]["used_gb"] if records else used
        daily_delta = used - prev_used

        records.append(
            dict(
                user_id=user_id,
                profile=profile,
                date=date.date().isoformat(),
                day_index=d,
                total_capacity_gb=float(capacity),
                used_gb=round(used, 4),
                free_gb=round(free, 4),
                used_pct=round(used_pct, 3),
                photos_gb=round(comps["photos"], 4),
                videos_gb=round(comps["videos"], 4),
                apps_gb=round(comps["apps"], 4),
                documents_gb=round(comps["documents"], 4),
                system_gb=round(comps["system"], 4),
                other_gb=round(comps["other"], 4),
                daily_delta_gb=round(daily_delta, 4),
                cleanup_event=int(cleanup),
            )
        )

    return records


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_records = []
    uid = 0
    for profile in PROFILES:
        for _ in range(USERS_PER_PROFILE):
            uid += 1
            all_records.extend(simulate_user(user_id=f"U{uid:03d}", profile=profile))

    df = pd.DataFrame(all_records)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"✓ Generated {len(df):,} rows")
    print(f"✓ Users: {df['user_id'].nunique()} across {df['profile'].nunique()} profiles")
    print(f"✓ Date range: {df['date'].min()} → {df['date'].max()}")
    print(f"✓ Saved to: {OUTPUT_CSV}")
    print(f"✓ Max used_pct: {df['used_pct'].max():.3f}")
    print(f"✓ Min free_gb: {df['free_gb'].min():.3f}")
    print("\n--- Sample rows ---")
    print(df.head(3).to_string(index=False))
    print("\n--- Per-profile summary (avg used_gb at end) ---")
    last_day = df["day_index"].max()
    summary = (
        df[df["day_index"] == last_day]
        .groupby("profile")[["used_gb", "used_pct", "cleanup_event"]]
        .agg({"used_gb": ["mean", "min", "max"], "used_pct": ["mean", "max"], "cleanup_event": "mean"})
        .round(2)
    )
    print(summary)


if __name__ == "__main__":
    main()
