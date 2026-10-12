"""
Module: collect_reviews.py
Purpose: Collects MoveInSync Google Play Store app metadata and public user reviews.
Target App: com.moveinsync.ets (Employee commute app)
"""

import os
import sys
import datetime
import pandas as pd
from google_play_scraper import app, reviews, Sort

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..")) if os.path.basename(CURRENT_DIR) == "analysis" else os.path.abspath(".")

APP_ID = "com.moveinsync.ets"
SOURCE_URL = f"https://play.google.com/store/apps/details?id={APP_ID}"
RAW_REVIEWS_PATH = os.path.join(PROJECT_ROOT, "data", "raw_reviews.csv")
SOURCE_LOG_PATH = os.path.join(PROJECT_ROOT, "report", "source_log.csv")

def collect_app_metadata():
    print(f"[*] Fetching app metadata for {APP_ID}...")
    try:
        app_info = app(APP_ID, lang="en", country="in")
    except Exception as e:
        print(f"[!] Error fetching app details: {e}")
        return None

    snapshot_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_date = datetime.datetime.fromtimestamp(app_info.get("updated", 0)).strftime("%Y-%m-%d %H:%M:%S") if app_info.get("updated") else "N/A"
    
    metadata = {
        "timestamp": snapshot_date,
        "app_name": app_info.get("title", "MoveInSync"),
        "package_id": APP_ID,
        "developer": app_info.get("developer", "MoveInSync: Enabling Hybrid Workplaces"),
        "store_rating": app_info.get("score", 0.0),
        "total_ratings": app_info.get("ratings", 0),
        "total_reviews_count": app_info.get("reviews", 0),
        "installs_estimate": app_info.get("realInstalls", 0),
        "app_version": app_info.get("version", "N/A"),
        "last_updated": updated_date,
        "source_url": SOURCE_URL,
        "collection_method": "google-play-scraper library (Public Google Play Store API endpoints)",
        "notes": f"Primary employee transportation application. Recent release notes: {str(app_info.get('recentChanges', ''))[:100]}"
    }

    df_meta = pd.DataFrame([metadata])
    os.makedirs(os.path.dirname(SOURCE_LOG_PATH), exist_ok=True)
    df_meta.to_csv(SOURCE_LOG_PATH, index=False)
    print(f"[+] App metadata saved to {SOURCE_LOG_PATH}")
    print(f"    Title: {metadata['app_name']}")
    print(f"    Rating: {metadata['store_rating']} ({metadata['total_ratings']} ratings)")
    print(f"    Installs: ~{metadata['installs_estimate']:,}")
    print(f"    Latest Version: {metadata['app_version']} (Updated: {metadata['last_updated']})")
    return metadata

def collect_reviews(target_count=1800):
    print(f"[*] Collecting public reviews for {APP_ID} (Target: ~{target_count})...")
    all_reviews = []
    seen_ids = set()
    collection_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Strategy: Gather from Sort.NEWEST (to capture recent 90-180 days and latest updates)
    # and Sort.MOST_RELEVANT (to capture high-engagement and impactful issues across ratings)
    sort_configs = [
        (Sort.NEWEST, 1000),
        (Sort.MOST_RELEVANT, 1000)
    ]

    for sort_order, sub_target in sort_configs:
        sort_name = "NEWEST" if sort_order == Sort.NEWEST else "MOST_RELEVANT"
        print(f"[*] Fetching up to {sub_target} reviews using Sort.{sort_name}...")
        continuation_token = None
        fetched_in_sort = 0

        while fetched_in_sort < sub_target:
            batch_count = min(200, sub_target - fetched_in_sort)
            try:
                res, continuation_token = reviews(
                    APP_ID,
                    lang="en",
                    country="in",
                    sort=sort_order,
                    count=batch_count,
                    continuation_token=continuation_token
                )
            except Exception as e:
                print(f"[!] Error fetching batch: {e}")
                break

            if not res:
                print("[-] No more reviews returned for this sort.")
                break

            for item in res:
                r_id = item.get("reviewId")
                if r_id and r_id not in seen_ids:
                    seen_ids.add(r_id)
                    all_reviews.append({
                        "review_id": r_id,
                        "review_date": item.get("at").strftime("%Y-%m-%d %H:%M:%S") if item.get("at") else None,
                        "star_rating": item.get("score"),
                        "review_text": item.get("content") or "",
                        "app_version": item.get("reviewCreatedVersion") or item.get("appVersion") or "Unknown",
                        "developer_response": item.get("replyContent"),
                        "developer_response_date": item.get("repliedAt").strftime("%Y-%m-%d %H:%M:%S") if item.get("repliedAt") else None,
                        "source_url": SOURCE_URL,
                        "collection_date": collection_ts
                    })
                    fetched_in_sort += 1

            print(f"    Batch fetched {len(res)} reviews (Total unique collected so far: {len(all_reviews)})")
            if continuation_token is None or len(all_reviews) >= target_count + 300:
                break

    df_reviews = pd.DataFrame(all_reviews)
    os.makedirs(os.path.dirname(RAW_REVIEWS_PATH), exist_ok=True)
    df_reviews.to_csv(RAW_REVIEWS_PATH, index=False)
    print(f"[+] Total {len(df_reviews)} raw reviews saved to {RAW_REVIEWS_PATH}")
    return df_reviews

if __name__ == "__main__":
    collect_app_metadata()
    collect_reviews(target_count=1800)
