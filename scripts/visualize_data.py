"""
Visualize synthetic storage dataset — produces a multi-panel chart showing
how each user profile behaves over time.
"""

import os
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

CSV_PATH = os.path.join("data", "synthetic", "synthetic_storage_usage.csv")
OUT_DIR = os.path.join("reports", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH, parse_dates=["date"])

profiles = ["media_heavy", "gamer", "office_user", "cleaner"]
colors = {
    "media_heavy": "#E63946",
    "gamer": "#457B9D",
    "office_user": "#2A9D8F",
    "cleaner": "#F4A261",
}

# 1) Per-profile storage growth
fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
axes = axes.flatten()
for i, profile in enumerate(profiles):
    ax = axes[i]
    sub = df[df["profile"] == profile]
    for _, grp in sub.groupby("user_id"):
        ax.plot(grp["date"], grp["used_gb"], alpha=0.7, linewidth=1.1, color=colors[profile])
    ax.set_title(f"{profile.replace('_', ' ').title()} (n={sub['user_id'].nunique()} users)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Used storage (GB)")
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
fig.suptitle("Synthetic Storage Usage — Per-Profile Patterns", fontsize=15, fontweight="bold", y=1.00)
plt.tight_layout()
out1 = os.path.join(OUT_DIR, "storage_per_profile.png")
plt.savefig(out1, dpi=130, bbox_inches="tight")
plt.close()
print(f"✓ Saved {out1}")

# 2) Average growth curve per profile
fig, ax = plt.subplots(figsize=(13, 6))
agg = df.groupby(["profile", "day_index"])["used_gb"].agg(["mean", "std"]).reset_index()
for profile in profiles:
    sub = agg[agg["profile"] == profile]
    ax.plot(sub["day_index"], sub["mean"], label=profile.replace("_", " ").title(), color=colors[profile], linewidth=2)
    ax.fill_between(sub["day_index"], sub["mean"] - sub["std"], sub["mean"] + sub["std"], color=colors[profile], alpha=0.15)
ax.set_title("Average Storage Growth by User Profile (mean ± 1σ)", fontsize=14, fontweight="bold")
ax.set_xlabel("Day index")
ax.set_ylabel("Used storage (GB)")
ax.grid(alpha=0.3)
ax.legend(loc="upper left", frameon=True)
plt.tight_layout()
out2 = os.path.join(OUT_DIR, "storage_avg_per_profile.png")
plt.savefig(out2, dpi=130, bbox_inches="tight")
plt.close()
print(f"✓ Saved {out2}")

# 3) Storage composition for one representative user per profile
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
axes = axes.flatten()
cats = ["system_gb", "apps_gb", "photos_gb", "videos_gb", "documents_gb", "other_gb"]
cat_colors = ["#6c757d", "#0077b6", "#e63946", "#f4a261", "#2a9d8f", "#9d4edd"]
for i, profile in enumerate(profiles):
    ax = axes[i]
    uid = df[df["profile"] == profile]["user_id"].unique()[0]
    sub = df[df["user_id"] == uid].sort_values("date")
    ax.stackplot(sub["date"], [sub[c] for c in cats], labels=[c.replace("_gb", "").title() for c in cats], colors=cat_colors, alpha=0.9)
    ax.set_title(f"{profile.replace('_', ' ').title()} — {uid}", fontsize=12, fontweight="bold")
    ax.set_ylabel("GB")
    ax.grid(alpha=0.3)
    if i == 0:
        ax.legend(loc="upper left", fontsize=8, ncol=2)
fig.suptitle("Storage Composition Over Time (one user per profile)", fontsize=15, fontweight="bold", y=1.00)
plt.tight_layout()
out3 = os.path.join(OUT_DIR, "storage_composition.png")
plt.savefig(out3, dpi=130, bbox_inches="tight")
plt.close()
print(f"✓ Saved {out3}")

print("\nAll figures generated successfully.")
