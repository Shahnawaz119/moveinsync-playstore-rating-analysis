"""
Module: analyze_reviews.py
Purpose: Performs comprehensive NLP sentiment classification, multi-label issue tagging,
         primary issue resolution, time-series aggregation, and cross-tabulation.
Input: data/cleaned_reviews.csv
Output: data/review_analysis.csv
"""

import os
import sys
import re
import pandas as pd
import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..")) if os.path.basename(CURRENT_DIR) == "analysis" else os.path.abspath(".")

CLEANED_PATH = os.path.join(PROJECT_ROOT, "data", "cleaned_reviews.csv")
ANALYSIS_PATH = os.path.join(PROJECT_ROOT, "data", "review_analysis.csv")

# Issue taxonomy definitions with comprehensive regex patterns
ISSUE_TAXONOMY = {
    "ETA & Timing Accuracy": [
        r"\beta\b", r"\bdelay\b", r"\bdelayed\b", r"\blate\b", r"\bpickup time\b", r"\bdrop time\b",
        r"\bwait time\b", r"\bwaiting\b", r"\btiming\b", r"\btimings\b", r"\bpunctual\b", r"\bpunctuality\b",
        r"\bexpected time\b", r"\btime accuracy\b", r"\bruns late\b", r"\balways late\b", r"\breach late\b",
        r"\btime estimation\b"
    ],
    "GPS & Live Tracking": [
        r"\bgps\b", r"\blive track\b", r"\btracking\b", r"\bwrong location\b", r"\blocation error\b",
        r"\bmap\b", r"\bmaps\b", r"\bvehicle location\b", r"\bcar location\b", r"\bnot moving\b",
        r"\bshows wrong\b", r"\bnavigation\b", r"\bpinpoint\b", r"\breal time\b", r"\blocation accuracy\b",
        r"\bjumpy\b", r"\bwrong direction\b", r"\bvan location\b", r"\blocation permission\b"
    ],
    "Booking & Schedule Management": [
        r"\bbooking\b", r"\bbook\b", r"\bcancel\b", r"\bcancellation\b", r"\bcan\'t book\b", r"\bcannot book\b",
        r"\bwaitlist\b", r"\bwaitlisted\b", r"\bmodify\b", r"\broster\b", r"\brostering\b", r"\bauto cancel\b",
        r"\bcut off\b", r"\bcutoff\b", r"\breschedule\b", r"\bno cab available\b", r"\bseat\b", r"\bseats\b",
        r"\badvance booking\b", r"\bfailed to book\b"
    ],
    "UI/UX & Forced Rating": [
        r"\bforcing\b", r"\bforce rating\b", r"\brating popup\b", r"\bunskippable\b", r"\bno skip\b",
        r"\brate the trip\b", r"\brating the trip\b", r"\bask for rating\b", r"\basking for rating\b",
        r"\bmandatory rating\b", r"\bgive rating after every ride\b", r"\bforce to rate\b",
        r"\bui\b", r"\bux\b", r"\binterface\b", r"\bconfusing\b", r"\bnew update\b", r"\bworse update\b",
        r"\bold version\b", r"\bpolicy acceptance\b", r"\bdesign\b", r"\bcomplicated\b", r"\bcluttered\b",
        r"\bdark mode\b", r"\bfont\b", r"\bbutton\b"
    ],
    "App Stability & Crashes": [
        r"\bcrash\b", r"\bcrashes\b", r"\bcrashing\b", r"\bforce close\b", r"\bfreeze\b", r"\bfrozen\b",
        r"\bfreezing\b", r"\buninstall\b", r"\breinstall\b", r"\bhang\b", r"\bhanging\b", r"\bnot opening\b",
        r"\bwon\'t open\b", r"\bcannot open\b", r"\bunable to open\b", r"\bcloses as soon as\b",
        r"\bauto close\b", r"\bauto closes\b", r"\bkeeps closing\b", r"\bblack screen\b", r"\bwhite screen\b",
        r"\blag\b", r"\blagging\b", r"\bbug\b", r"\bbuggy\b", r"\bglitch\b", r"\bstuck\b"
    ],
    "Driver Behavior & Safety": [
        r"\brash\b", r"\brude\b", r"\barrogant\b", r"\bunsafe\b", r"\bspeeding\b", r"\babuse\b",
        r"\babusive\b", r"\bcareless driver\b", r"\blate night safety\b", r"\bescort\b", r"\bsecurity\b",
        r"\bsos\b", r"\bpanic\b", r"\bthreat\b", r"\bbad driving\b", r"\brash driving\b",
        r"\bdriver behavior\b", r"\bdriver behaviour\b", r"\brude driver\b", r"\bunprofessional driver\b"
    ],
    "Routing & Detour Inefficiency": [
        r"\broute\b", r"\brouting\b", r"\broutes\b", r"\blong route\b", r"\blongest route\b", r"\bdetour\b",
        r"\broundabout\b", r"\bpickup point\b", r"\bdistance\b", r"\bwalking\b", r"\bwalk\b", r"\bstop\b",
        r"\bextra time\b", r"\btravel time\b", r"\bcommute time\b", r"\bclubbing\b", r"\bclubbed\b"
    ],
    "Helpdesk & Support Responsiveness": [
        r"\bsupport\b", r"\bhelpdesk\b", r"\btransport desk\b", r"\bcustomer service\b", r"\bhelpline\b",
        r"\bcall center\b", r"\bno response\b", r"\bnot helpful\b", r"\bticket\b", r"\bexecutive\b",
        r"\bcomplaint\b", r"\bunhelpful\b", r"\bno help\b", r"\bcustomer care\b"
    ],
    "OTP, Boarding & Check-In": [
        r"\botp\b", r"\bcheck in\b", r"\bcheckin\b", r"\bboard\b", r"\bboarding\b", r"\bqr\b", r"\bscan\b",
        r"\bscanner\b", r"\bno-show\b", r"\bnoshow\b", r"\bseat belt\b", r"\bseatbelt\b", r"\bcode\b"
    ],
    "Login, SSO & Authentication": [
        r"\blogin\b", r"\blog in\b", r"\bsign in\b", r"\bsso\b", r"\bpassword\b", r"\bcredential\b",
        r"\bauthentication\b", r"\bregister\b", r"\bregistration\b", r"\baccount\b", r"\bdomain\b"
    ],
    "Notifications & Alerts": [
        r"\bnotification\b", r"\bnotifications\b", r"\balert\b", r"\balerts\b", r"\bsms\b", r"\bpush notification\b",
        r"\bno alert\b", r"\blate alert\b", r"\bghost notification\b", r"\bmessage\b"
    ],
    "Cab & Driver Allocation": [
        r"\bcab not assigned\b", r"\bvehicle not assigned\b", r"\bno cab assigned\b", r"\ballocation\b",
        r"\ballocated\b", r"\bassignment\b", r"\blast minute\b", r"\bno vehicle\b", r"\bno driver assigned\b"
    ]
}

# Positive lexicon
POSITIVE_PATTERNS = [
    r"\bgood\b", r"\bgreat\b", r"\bexcellent\b", r"\bawesome\b", r"\bbest\b", r"\bsmooth\b",
    r"\beasy\b", r"\bhelpful\b", r"\bconvenient\b", r"\bcomfortable\b", r"\bnice\b", r"\bsafe\b",
    r"\blove\b", r"\bfantastic\b", r"\bwell\b", r"\bpunctual\b", r"\bon time\b", r"\buser friendly\b"
]

def determine_sentiment(star_rating, text_polarity):
    if star_rating >= 4:
        return "Positive"
    elif star_rating == 3:
        if text_polarity > 0.1:
            return "Positive"
        elif text_polarity < -0.1:
            return "Negative"
        return "Neutral"
    else:
        return "Negative"

def classify_review(row):
    text = row["cleaned_text"]
    star = row["star_rating"]

    matched_issues = []
    for issue, patterns in ISSUE_TAXONOMY.items():
        combined = "|".join(patterns)
        if re.search(combined, text):
            matched_issues.append(issue)

    # Determine polarity score roughly
    pos_matches = sum(1 for p in POSITIVE_PATTERNS if re.search(p, text))
    neg_matches = len(matched_issues)
    total_signals = pos_matches + neg_matches
    polarity = (pos_matches - neg_matches) / max(total_signals, 1)

    sentiment = determine_sentiment(star, polarity)

    # Determine primary issue
    if star >= 4:
        if len(matched_issues) == 0 or pos_matches >= len(matched_issues):
            primary_issue = "Positive Experience"
        else:
            primary_issue = "Positive Experience (Minor Friction)"
    elif len(matched_issues) > 0:
        # Prioritize issues by engineering criticality
        # Stability > Safety/Driver > ETA/Timing > GPS > Forced Rating > Booking > Detour > OTP > Login > Support > Notifications > Allocation
        priority_order = [
            "App Stability & Crashes",
            "Driver Behavior & Safety",
            "ETA & Timing Accuracy",
            "GPS & Live Tracking",
            "UI/UX & Forced Rating",
            "Booking & Schedule Management",
            "Routing & Detour Inefficiency",
            "OTP, Boarding & Check-In",
            "Login, SSO & Authentication",
            "Helpdesk & Support Responsiveness",
            "Notifications & Alerts",
            "Cab & Driver Allocation"
        ]
        chosen = None
        for p in priority_order:
            if p in matched_issues:
                chosen = p
                break
        primary_issue = chosen if chosen else matched_issues[0]
    else:
        if star <= 2:
            primary_issue = "General Dissatisfaction (Unspecified)"
        elif star == 3:
            primary_issue = "Mixed / Neutral Experience"
        else:
            primary_issue = "Positive Experience"

    issue_tags_str = "; ".join(matched_issues) if matched_issues else "None"
    issue_count = len(matched_issues)

    return pd.Series({
        "sentiment": sentiment,
        "polarity_score": round(polarity, 2),
        "primary_issue": primary_issue,
        "issue_tags": issue_tags_str,
        "issue_count": issue_count
    })

def run_analysis():
    print(f"[*] Reading cleaned reviews from {CLEANED_PATH}...")
    df = pd.read_csv(CLEANED_PATH)

    print("[*] Running sentiment, topic classification, and multi-label tagging...")
    classification_results = df.apply(classify_review, axis=1)
    df = pd.concat([df, classification_results], axis=1)

    # Add severity weighting
    # P0/Critical: Safety, Crashes
    # P1/High: ETA, GPS Tracking, Booking, Forced Rating Popup
    # P2/Medium: Detour Routing, Support, OTP, Login, Notifications
    severity_map = {
        "Driver Behavior & Safety": "High Severity / Safety Critical",
        "App Stability & Crashes": "High Severity / Core Functional Defect",
        "ETA & Timing Accuracy": "High Severity / Commute Failure",
        "GPS & Live Tracking": "High Severity / Real-Time Failure",
        "UI/UX & Forced Rating": "Medium-High Severity / Rating Bias Inducer",
        "Booking & Schedule Management": "High Severity / Workflow Blocker",
        "Routing & Detour Inefficiency": "Medium Severity / Commute Fatigue",
        "OTP, Boarding & Check-In": "Medium Severity / Boarding Friction",
        "Helpdesk & Support Responsiveness": "Medium Severity / Escalation Defect",
        "Login, SSO & Authentication": "Medium Severity / Auth Friction",
        "Notifications & Alerts": "Low-Medium Severity / Communication Lag",
        "Cab & Driver Allocation": "High Severity / Service Inavailability",
        "Positive Experience": "None (Positive)",
        "Positive Experience (Minor Friction)": "None (Positive with Notes)",
        "General Dissatisfaction (Unspecified)": "Low Severity / Vague",
        "Mixed / Neutral Experience": "Low Severity / Neutral"
    }
    df["severity_class"] = df["primary_issue"].map(severity_map).fillna("Unclassified")

    os.makedirs(os.path.dirname(ANALYSIS_PATH), exist_ok=True)
    df.to_csv(ANALYSIS_PATH, index=False)
    print(f"[+] Review analysis dataset saved to {ANALYSIS_PATH} ({len(df)} records)")

    # Print summary statistics
    print("\n" + "="*50)
    print("=== OVERALL RATING & SENTIMENT BREAKDOWN ===")
    print("="*50)
    print(df["star_rating"].value_counts().sort_index().rename("Count").to_frame().assign(
        Percentage=lambda x: (x["Count"] / len(df) * 100).round(2)
    ))
    
    print("\n=== SENTIMENT DISTRIBUTION ===")
    print(df["sentiment"].value_counts().rename("Count").to_frame().assign(
        Percentage=lambda x: (x["Count"] / len(df) * 100).round(2)
    ))

    print("\n=== TOP PRIMARY ISSUES (ALL REVIEWS) ===")
    print(df["primary_issue"].value_counts().head(12))

    print("\n=== TOP PRIMARY ISSUES IN NEGATIVE REVIEWS (1-2 STARS) ===")
    neg_df = df[df["star_rating"] <= 2]
    print(neg_df["primary_issue"].value_counts().head(10).rename("Negative Reviews").to_frame().assign(
        Pct_Of_Negative=lambda x: (x["Negative Reviews"] / len(neg_df) * 100).round(2)
    ))

    # Validation sample output
    print("\n" + "="*50)
    print("=== CLASSIFICATION VALIDATION SAMPLE (10 RANDOM REVIEWS) ===")
    print("="*50)
    sample = df.sample(10, random_state=42)[["review_date", "star_rating", "primary_issue", "issue_tags", "review_text"]]
    for idx, r in sample.iterrows():
        print(f"⭐ {r['star_rating']} | Primary: {r['primary_issue']}")
        print(f"   Tags: {r['issue_tags']}")
        print(f"   Text: {r['review_text'][:120]}...\n")

    return df

if __name__ == "__main__":
    run_analysis()
