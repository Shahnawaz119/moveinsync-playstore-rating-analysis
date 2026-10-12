"""
Unit & Integration Test Suite for MoveInSync Play Store Ratings Case Study
Tests:
  - File presence and schema completeness
  - Data integrity & PII redaction
  - Mathematical & statistical consistency
  - Classification pipeline rules and accuracy
  - Output visualization artifacts
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

import pytest
import pandas as pd
import numpy as np

RAW_PATH = os.path.join("data", "raw_reviews.csv")
CLEANED_PATH = os.path.join("data", "cleaned_reviews.csv")
ANALYSIS_PATH = os.path.join("data", "review_analysis.csv")
SOURCE_LOG_PATH = os.path.join("report", "source_log.csv")

def test_file_existence():
    """Verify all generated data and logging artifacts exist."""
    assert os.path.exists(RAW_PATH), f"Missing {RAW_PATH}"
    assert os.path.exists(CLEANED_PATH), f"Missing {CLEANED_PATH}"
    assert os.path.exists(ANALYSIS_PATH), f"Missing {ANALYSIS_PATH}"
    assert os.path.exists(SOURCE_LOG_PATH), f"Missing {SOURCE_LOG_PATH}"

def test_source_log_content():
    """Verify app metadata snapshot is logged accurately."""
    df_meta = pd.read_csv(SOURCE_LOG_PATH)
    assert not df_meta.empty, "Source log is empty"
    row = df_meta.iloc[0]
    assert row["package_id"] == "com.moveinsync.ets"
    assert "MoveInSync" in str(row["app_name"])
    assert float(row["store_rating"]) > 4.0
    assert int(row["total_ratings"]) > 50000

def test_cleaned_data_integrity():
    """Verify cleaned reviews schema, row counts, deduplication, and bounds."""
    df_clean = pd.read_csv(CLEANED_PATH)
    assert len(df_clean) >= 500, "Cleaned dataset contains fewer than 500 records"
    assert len(df_clean) == df_clean["review_id"].nunique(), "Duplicate review_ids found"
    
    # Rating bounds
    assert df_clean["star_rating"].isin([1, 2, 3, 4, 5]).all(), "Found invalid star ratings"
    
    # Text validity
    assert df_clean["review_text"].notna().all(), "Found null review texts"
    assert (df_clean["review_text"].str.strip() != "").all(), "Found empty review texts"
    
    # Date format
    dates = pd.to_datetime(df_clean["review_date"], errors="coerce")
    assert dates.notna().all(), "Unparseable review dates detected"

def test_pii_redaction():
    """Verify phone numbers and emails are masked in review text."""
    from analysis.clean_reviews import mask_pii
    sample_text = "Call driver at 9876543210 or email test@example.com for my ride"
    masked = mask_pii(sample_text)
    assert "9876543210" not in masked
    assert "test@example.com" not in masked
    assert "[REDACTED_PHONE]" in masked
    assert "[REDACTED_EMAIL]" in masked

def test_statistical_consistency():
    """Verify mathematical properties of ratings and sentiment breakdowns."""
    df = pd.read_csv(ANALYSIS_PATH)
    total = len(df)
    
    rating_counts = df["star_rating"].value_counts()
    assert rating_counts.sum() == total, "Rating counts do not sum to total records"
    
    sentiment_counts = df["sentiment"].value_counts()
    assert sentiment_counts.sum() == total, "Sentiment counts do not sum to total records"
    
    # Sample mean calculation check
    expected_mean = df["star_rating"].sum() / total
    assert np.isclose(df["star_rating"].mean(), expected_mean, atol=1e-5)

def test_classification_pipeline():
    """Verify issue classification taxonomy on representative domain phrases."""
    from analysis.analyze_reviews import classify_review
    
    # Test crash phrase
    test_row_crash = pd.Series({
        "cleaned_text": "app crashes repeatedly on startup after update",
        "star_rating": 1
    })
    res_crash = classify_review(test_row_crash)
    assert res_crash["primary_issue"] == "App Stability & Crashes"
    assert res_crash["sentiment"] == "Negative"
    
    # Test forced rating phrase
    test_row_rating = pd.Series({
        "cleaned_text": "forcing me to give rating after every ride with no skip option",
        "star_rating": 1
    })
    res_rating = classify_review(test_row_rating)
    assert res_rating["primary_issue"] == "UI/UX & Forced Rating"
    
    # Test positive phrase
    test_row_pos = pd.Series({
        "cleaned_text": "smooth and safe ride excellent professional driver on time",
        "star_rating": 5
    })
    res_pos = classify_review(test_row_pos)
    assert res_pos["sentiment"] == "Positive"
    assert "Positive Experience" in res_pos["primary_issue"]

def test_output_charts_exist():
    """Verify all 4 required visualization deliverables exist and are non-empty."""
    charts = [
        os.path.join("outputs", "rating_distribution.png"),
        os.path.join("outputs", "rating_trend.png"),
        os.path.join("outputs", "issue_frequency.png"),
        os.path.join("outputs", "priority_matrix.png")
    ]
    for c in charts:
        assert os.path.exists(c), f"Chart {c} was not generated"
        assert os.path.getsize(c) > 10000, f"Chart {c} appears truncated or empty"
