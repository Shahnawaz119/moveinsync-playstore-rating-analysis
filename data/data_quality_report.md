# MoveInSync Play Store Reviews — Data Quality & Integrity Report

**Report Generated:** 2026-10-12 14:05:25  
**Target Package:** `com.moveinsync.ets`  
**Dataset Path:** `data\cleaned_reviews.csv`

---

## 1. Data Ingestion & Sanitization Summary

| Metric | Value | Status / Notes |
| :--- | :--- | :--- |
| **Raw Records Ingested** | **2,139** | Direct scrape from Google Play Store API |
| **Duplicate Records Removed** | **0** | Identified via unique `review_id` hash |
| **Invalid Star Ratings Filtered** | **0** | Verified range [1, 2, 3, 4, 5] |
| **Invalid / Unparseable Dates** | **0** | Standardized to ISO 8601 |
| **Final Cleaned Record Count** | **2,139** | 100% complete and validated |
| **Date Range Covered** | **2018-09-14** to **2026-10-11** | Over 8 years historical depth with high recent density |

---

## 2. Rating Distribution Profile (Sampled Data)

| Star Rating | Record Count | Sample Share (%) | Rating Sentiment Band |
| :---: | :---: | :---: | :--- |
| ⭐ 1 Star | 877 | 41.0% | Critical Dissatisfaction |
| ⭐ 2 Stars | 152 | 7.11% | Severe Friction |
| ⭐ 3 Stars | 136 | 6.36% | Neutral / Mixed Usability |
| ⭐ 4 Stars | 183 | 8.56% | Satisfactory Commute |
| ⭐ 5 Stars | 791 | 36.98% | Promoter / Positive Experience |
| **Total** | **2,139** | **100.0%** | **Sample Average: 2.93 / 5.00** |

> **Key Distinction:**
> The sampled review average (2.93 / 5.0) reflects **written textual reviews**, where users disproportionately submit written feedback during commute disruptions. This is distinct from Google Play's lifetime aggregate rating of **4.64 / 5.0** across 114,878+ silent and star-only ratings.

---

## 3. Completeness & Attribute Integrity

| Field Name | Non-Null Count | Completeness (%) | Data Type | Notes |
| :--- | :---: | :---: | :--- | :--- |
| `review_id` | 2,139 | 100.0% | String (UUID) | Unique identifier |
| `review_date` | 2,139 | 100.0% | Datetime | Parsed timestamp |
| `star_rating` | 2,139 | 100.0% | Integer | Bound within [1..5] |
| `review_text` | 2,139 | 100.0% | String | Preserved original text |
| `cleaned_text` | 2,139 | 100.0% | String | Lowercased, stripped, PII-masked |
| `app_version` | 2,139 | 100.0% | String | 164 distinct versions; 8.7% unknown |
| `developer_response` | 542 | 25.34% | String | Public responses from MoveInSync developer |
| `response_delay_days` | 542 | 25.34% | Float | Median response turnaround: 1.0 days |
| `word_count` | 2,139 | 100.0% | Integer | Min: 1, Median: 25.0, Max: 115 words |

---

## 4. Privacy, PII Protection & Compliance Audit

- **Reviewer Identifiers:** Reviewer usernames and user images were stripped during collection to ensure privacy and GDPR/DPDP alignment.
- **Sensitive Text Masking:** Regular expressions scanned and redacted phone numbers, email addresses, and potential OTP/Employee IDs from the review content.
- **Access Compliance:** Data was retrieved via public Google Play Store web endpoints without bypassing CAPTCHAs, paywalls, or authenticated personal credentials.
