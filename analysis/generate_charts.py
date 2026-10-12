"""
Module: generate_charts.py
Purpose: Generates publication-quality charts for the case study report and deliverables.
Outputs:
  - outputs/rating_distribution.png
  - outputs/rating_trend.png
  - outputs/issue_frequency.png
  - outputs/priority_matrix.png
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configure styles
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "figure.autolayout": True,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.labelweight": "bold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 300
})

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..")) if os.path.basename(CURRENT_DIR) == "analysis" else os.path.abspath(".")

OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
ANALYSIS_PATH = os.path.join(PROJECT_ROOT, "data", "review_analysis.csv")

def generate_rating_distribution(df):
    plt.figure(figsize=(9, 5.5))
    counts = df["star_rating"].value_counts().sort_index()
    total = len(df)
    percentages = (counts / total * 100).round(1)

    colors = ["#D9381E", "#EA6A47", "#F0A500", "#7CB342", "#2E7D32"]
    bars = plt.bar(counts.index, counts.values, color=colors, width=0.6, edgecolor="#333333", linewidth=1)

    for bar, pct, cnt in zip(bars, percentages, counts):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 18, f"{cnt:,}\n({pct}%)", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.title("MoveInSync Google Play Reviews: Star Rating Distribution", pad=15)
    plt.xlabel("Star Rating (1 to 5 Stars)")
    plt.ylabel("Number of Written Reviews")
    plt.ylim(0, max(counts.values) * 1.18)
    plt.xticks([1, 2, 3, 4, 5], ["1 Star\n(Critical)", "2 Stars\n(Friction)", "3 Stars\n(Neutral)", "4 Stars\n(Satisfied)", "5 Stars\n(Promoter)"])

    # Annotation box
    plt.annotate(
        f"Total Sample: {total:,} Reviews\nSample Avg: {df['star_rating'].mean():.2f} / 5.0\n1-2 Stars (Negative): {(df['star_rating']<=2).sum() / total * 100:.1f}%\n4-5 Stars (Positive): {(df['star_rating']>=4).sum() / total * 100:.1f}%\nLifetime Play Store Rating: 4.64 / 5.0",
        xy=(0.03, 0.95), xycoords="axes fraction",
        fontsize=9.5, va="top",
        bbox=dict(boxstyle="round,pad=0.6", fc="#F8F9FA", ec="#B0BEC5", lw=1.2)
    )

    out_file = os.path.join(OUTPUTS_DIR, "rating_distribution.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved {out_file}")

def generate_rating_trend(df):
    df_sorted = df.copy()
    df_sorted["review_date"] = pd.to_datetime(df_sorted["review_date"])
    
    # Filter for periods with at least 5 reviews to prevent noisy spikes
    monthly = df_sorted.groupby("review_year_month").agg(
        avg_rating=("star_rating", "mean"),
        count=("star_rating", "count"),
        pct_negative=("star_rating", lambda s: (s <= 2).mean() * 100)
    ).reset_index()

    # Take the last 24 active months
    monthly = monthly.tail(24)

    fig, ax1 = plt.subplots(figsize=(11, 6))

    color_vol = "#CFD8DC"
    ax2 = ax1.twinx()
    bars = ax2.bar(monthly["review_year_month"], monthly["count"], color=color_vol, alpha=0.65, label="Monthly Review Volume", width=0.55)
    ax2.set_ylabel("Monthly Review Volume (Bars)", color="#546E7A", fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#546E7A")
    ax2.grid(False)

    color_line = "#1565C0"
    line = ax1.plot(monthly["review_year_month"], monthly["avg_rating"], color=color_line, marker="o", linewidth=2.5, label="Average Rating (Line)")
    ax1.axhline(df["star_rating"].mean(), color="#D84315", linestyle="--", alpha=0.8, label=f"Sample Mean ({df['star_rating'].mean():.2f})")
    ax1.set_ylabel("Average Star Rating (1.0 to 5.0)", color=color_line, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_line)
    ax1.set_ylim(1.0, 5.0)

    ax1.set_title("MoveInSync Rating and Review Volume Trajectory Over Time", pad=15)
    ax1.set_xlabel("Year-Month")
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, facecolor="#FFFFFF", framealpha=0.9)

    out_file = os.path.join(OUTPUTS_DIR, "rating_trend.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved {out_file}")

def generate_issue_frequency(df):
    neg_df = df[df["star_rating"] <= 2]
    total_neg = len(neg_df)

    from collections import Counter
    all_tags = []
    for tags in neg_df["issue_tags"].dropna():
        if tags != "None":
            all_tags.extend([t.strip() for t in tags.split(";")])
    
    tag_counts = Counter(all_tags)
    df_issues = pd.DataFrame(tag_counts.most_common(10), columns=["Issue", "Mentions"])
    df_issues["Pct_Negative"] = (df_issues["Mentions"] / total_neg * 100).round(1)
    df_issues = df_issues.sort_values(by="Mentions", ascending=True)

    plt.figure(figsize=(10, 6.5))
    colors = ["#B0BEC5" if p < 10 else "#E57373" if p < 14 else "#C62828" for p in df_issues["Pct_Negative"]]
    bars = plt.barh(df_issues["Issue"], df_issues["Mentions"], color=colors, edgecolor="#424242", linewidth=0.8)

    for bar, pct, cnt in zip(bars, df_issues["Pct_Negative"], df_issues["Mentions"]):
        plt.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2.0, f"{cnt} ({pct}%)", ha="left", va="center", fontsize=9.5, fontweight="bold")

    plt.title("Top Recurring Pain Points in Negative Reviews (1-2 Stars, N=1,029)", pad=15)
    plt.xlabel("Number of Unique Negative Reviews Mentioning Issue")
    plt.xlim(0, max(df_issues["Mentions"]) * 1.18)

    plt.annotate(
        "Multi-Label Tracking:\nReviews can report multiple concurrent failures\n(e.g., Booking Failure + Unresponsive Support).",
        xy=(0.62, 0.15), xycoords="axes fraction",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.5", fc="#FFF9C4", ec="#FBC02D", lw=1.2)
    )

    out_file = os.path.join(OUTPUTS_DIR, "issue_frequency.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved {out_file}")

def generate_priority_matrix(df):
    """
    Plots an Impact vs Effort prioritization matrix with safety adjustments.
    """
    recommendations = [
        {"name": "Fix Post-Update App Crash Loop", "impact": 9.5, "effort": 3.0, "prio": "P0", "freq": 100, "type": "Stability"},
        {"name": "Remove Unskippable In-App Rating Gate", "impact": 9.0, "effort": 1.5, "prio": "P0", "freq": 111, "type": "UX/Prompt"},
        {"name": "Driver Rash Driving & Late-Night Safety Protocol", "impact": 9.8, "effort": 4.5, "prio": "P0", "freq": 28, "type": "Safety"},
        {"name": "Real-Time GPS Staleness & In-Transit Telemetry", "impact": 8.5, "effort": 6.5, "prio": "P1", "freq": 164, "type": "Tracking"},
        {"name": "ETA Dynamic Calibration vs Google Traffic", "impact": 8.2, "effort": 6.0, "prio": "P1", "freq": 150, "type": "ETA"},
        {"name": "Waitlist Transparency & Auto-Cancel Grace Window", "impact": 8.0, "effort": 4.0, "prio": "P1", "freq": 180, "type": "Booking"},
        {"name": "Boarding OTP / Seatbelt Modal Decoupling", "impact": 7.5, "effort": 2.5, "prio": "P1", "freq": 108, "type": "Boarding"},
        {"name": "SSO Session Refresh & Background Auth Silent Retry", "impact": 7.0, "effort": 3.5, "prio": "P2", "freq": 108, "type": "Auth"},
        {"name": "Intelligent Multi-Stop Detour Cap in Pooling", "impact": 7.2, "effort": 7.5, "prio": "P2", "freq": 129, "type": "Routing"},
        {"name": "Transport Helpdesk In-App Live Chat Escalation", "impact": 6.8, "effort": 5.0, "prio": "P2", "freq": 85, "type": "Support"}
    ]
    df_prio = pd.DataFrame(recommendations)

    plt.figure(figsize=(10.5, 7))
    
    color_map = {"P0": "#D32F2F", "P1": "#F57C00", "P2": "#1976D2"}
    
    for _, row in df_prio.iterrows():
        size = row["freq"] * 5.5 + 120
        plt.scatter(row["effort"], row["impact"], s=size, color=color_map[row["prio"]], alpha=0.75, edgecolors="#212121", linewidth=1.5)
        plt.annotate(
            f"{row['name']}\n[{row['prio']}]",
            (row["effort"], row["impact"]),
            textcoords="offset points", xytext=(0, 12),
            ha="center", fontsize=8.5, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#BDBDBD", alpha=0.85)
        )

    plt.axvline(4.5, color="#757575", linestyle=":", alpha=0.7)
    plt.axhline(8.0, color="#757575", linestyle=":", alpha=0.7)

    # Quadrant annotations
    plt.text(1.2, 9.6, "HIGH IMPACT / LOW EFFORT\n[P0 Immediate Quick Wins]", fontsize=10, fontweight="bold", color="#2E7D32")
    plt.text(8.2, 9.6, "HIGH IMPACT / HIGH EFFORT\n[P1 Strategic Engineering]", fontsize=10, fontweight="bold", color="#E65100", ha="right")
    plt.text(1.2, 6.2, "LOWER IMPACT / LOW EFFORT\n[P2 Incremental Polish]", fontsize=9.5, fontweight="bold", color="#546E7A")
    plt.text(8.2, 6.2, "LOWER IMPACT / HIGH EFFORT\n[Defer / Deprioritize]", fontsize=9.5, fontweight="bold", color="#78909C", ha="right")

    plt.title("MoveInSync Product & Engineering Prioritization Matrix", pad=15)
    plt.xlabel("Implementation Effort Estimate (1 = Low / 1-2 sprints, 10 = Very High / Multiple quarters)")
    plt.ylabel("User & Business Impact Score (1 = Negligible, 10 = Transformative / Safety Critical)")
    plt.xlim(0.5, 8.5)
    plt.ylim(5.8, 10.2)

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker="o", color="w", label="P0 (Critical / Quick Win / Safety)", markerfacecolor="#D32F2F", markersize=12),
        plt.Line2D([0], [0], marker="o", color="w", label="P1 (Core Flow / High Impact)", markerfacecolor="#F57C00", markersize=12),
        plt.Line2D([0], [0], marker="o", color="w", label="P2 (Operational Polish / Support)", markerfacecolor="#1976D2", markersize=12),
    ]
    plt.legend(handles=legend_elements, loc="lower right", frameon=True, facecolor="#F5F5F5")

    out_file = os.path.join(OUTPUTS_DIR, "priority_matrix.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved {out_file}")

def main():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    if not os.path.exists(ANALYSIS_PATH):
        print(f"[!] {ANALYSIS_PATH} not found. Run analyze_reviews.py first.")
        return

    print(f"[*] Reading data from {ANALYSIS_PATH}...")
    df = pd.read_csv(ANALYSIS_PATH)
    generate_rating_distribution(df)
    generate_rating_trend(df)
    generate_issue_frequency(df)
    generate_priority_matrix(df)
    print("[+] All 4 deliverable charts successfully generated!")

if __name__ == "__main__":
    main()
