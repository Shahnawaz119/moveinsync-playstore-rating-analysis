# MoveInSync Play Store Ratings — Methodology & Tools Documentation

**Role:** Forward Deployed Engineer & Product Analyst  
**Application Target:** MoveInSync (`com.moveinsync.ets`)  
**Date of Snapshot:** October 2026  
**Environment:** Python 3.14 / Windows

---

## 1. Data Origin & Ingestion Architecture

### 1.1 Target Package Isolation
The research exclusively examined MoveInSync's primary employee-facing Android application:
- **Application Name:** MoveInSync
- **Package ID:** `com.moveinsync.ets`
- **Developer:** MoveInSync: Enabling Hybrid Workplaces
- **Store URL:** [Google Play Store Listing](https://play.google.com/store/apps/details?id=com.moveinsync.ets)

*Boundary Enforcement:* Driver partner applications (`com.moveinsync.driver`), field operations, and onboarding tools were strictly excluded to ensure that review findings directly reflect employee commute experiences.

### 1.2 Public Collection Mechanism
- **Scraping Tool:** `google-play-scraper` (v1.2.7), querying official Google Play Store web endpoints.
- **Collection Strategy:** To prevent recency bias while capturing critical historical pain points, data collection executed dual pagination passes:
  1. `Sort.NEWEST`: Captured recent 90–180 days of reviews to evaluate the immediate impact of recent app versions (e.g., `v12.19.x`).
  2. `Sort.MOST_RELEVANT`: Captured historically upvoted, high-engagement reviews across all rating bands.
- **Compliance & Rate Limiting:** All requests utilized standard HTTP payloads without bypassing CAPTCHAs, paywalls, or authenticated user sessions.
- **Sample Size:** **2,139 unique reviews** collected spanning from September 2018 through October 11, 2026.

---

## 2. Data Cleansing, Sanitization & PII Protection

The cleaning pipeline (`analysis/clean_reviews.py`) executed the following deterministic stages:
1. **Deduplication:** Hash-indexed deduplication on `review_id` ensured zero redundant rows across scraper sorts.
2. **Bounds Validation:** Star ratings were strictly filtered within $[1, 5]$. Dates were normalized to ISO 8601 timestamps (`YYYY-MM-DD HH:MM:SS`).
3. **Privacy & PII Redaction:** 
   - Personal reviewer names and avatar URLs were stripped during ingestion.
   - Text scanning masked Indian 10-digit phone numbers (`[REDACTED_PHONE]`), email addresses (`[REDACTED_EMAIL]`), and employee/OTP numbers (`[REDACTED_ID]`).
4. **Enrichment:** Engineered temporal features (`review_year_month`, `review_day_of_week`), text metrics (`char_length`, `word_count`), and developer response turnaround latency (`response_delay_days`).

---

## 3. NLP Classification & Issue Taxonomy

The analysis pipeline (`analysis/analyze_reviews.py`) applied a hybrid rule-based NLP framework designed for high interpretability and precision:

### 3.1 Issue Domain Mapping
Reviews were scanned against 12 domain dictionaries using compiled regular expressions:
- `App Stability & Crashes`: Launch crashes, freeze/hang, auto-close, uninstall/reinstall loops.
- `UI/UX & Forced Rating`: Mandatory post-ride rating modals, confusing updates, dark mode, policy modals.
- `GPS & Live Tracking`: Stale vehicle markers, map lag, jumpy navigation, tracking restrictions.
- `ETA & Timing Accuracy`: Pick-up/drop delays, static ETA vs. live traffic divergence.
- `Booking & Schedule Management`: Roster locking, waitlist ambiguity, auto-cancellations.
- `Routing & Detour Inefficiency`: Multi-stop pooling detours, cross-city passenger clubbing.
- `OTP, Boarding & Check-In`: OTP view hidden by seatbelt popups, QR scan failures.
- `Driver Behavior & Safety`: Rash driving, speeding, rude conduct, late-night escort absence.
- `Helpdesk & Support Responsiveness`: Unresponsive transport desks, unanswered emergency calls.
- `Login, SSO & Authentication`: SSO timeout, credential failure, login OTP delays.
- `Notifications & Alerts`: Delayed cab allocation SMS, ghost notifications.
- `Cab & Driver Allocation`: Last-minute vehicle unavailability, unassigned trips.

### 3.2 Multi-Label vs. Primary Issue Tagging
- **Multi-Label Mentions:** Every review was tagged with all matching issues to reflect compounded commute failures (e.g., Booking Failure + Unhelpful Transport Desk).
- **Primary Issue Resolution:** Negative reviews were assigned a single primary defect using an engineering severity hierarchy (`App Stability` > `Driver Safety` > `ETA` > `GPS` > `Forced Rating` > `Booking` > `Routing` > `Boarding` > `Auth` > `Support`).
- **Promoter Disambiguation:** 4-star and 5-star reviews mentioning drivers or punctuality were explicitly classified under `Positive Experience` rather than negative failure categories.

---

## 4. Analytical Tools & Environment Stack

| Category | Library / Tool | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Data Scraping** | `google-play-scraper` | 1.2.7 | Public Google Play API ingestion |
| **Data Processing** | `pandas`, `numpy` | 3.0.6, 2.5.4 | Data wrangling, aggregation, cleaning |
| **Statistical Analysis** | `scikit-learn`, `scipy` | 1.9.1, 1.18.1 | Distribution modeling & text statistics |
| **Visualizations** | `matplotlib`, `seaborn` | 3.11.2, 0.13.2 | Static publication-grade chart generation |
| **Interactive UI** | `streamlit`, `altair` | 1.65.0, 6.3.0 | Real-time CX dashboard development |
| **Quality Testing** | `pytest` | 9.1.1 | Unit and integration test verification |
| **Report Generation** | `reportlab` | 5.0.1 | Automated PDF compilation |

---

## 5. Scope Boundaries & Internal Telemetry Limitations

Public Play Store review data provides invaluable signal regarding user perception and operational friction, but possesses inherent boundaries:

| Dimension | Measurable from Public Data | Requires Internal MoveInSync Access |
| :--- | :--- | :--- |
| **User Complaints** | High-volume verbatim symptom descriptions | Verified reproduction steps and device logs |
| **App Crashes** | User reports of crashes and reinstall loops | Crashlytics stack traces, native symbols, ANR rate |
| **GPS Tracking Lag** | Stagnant vehicle marker complaints | MQTT broker latency, driver app background sleep metrics |
| **ETA Inaccuracy** | Perceived delay vs Google Maps comparisons | Internal routing engine logs vs ground-truth GPS telemetry |
| **Booking Cut-Offs** | User frustration over auto-cancellations | Employer-specific transport policy configurations |
| **Safety Escalations** | Public reviews citing rash driving or missing escorts | Fleet telematics (OBD-II accelerometer) and SOS desk tickets |

---

## 6. How to Rerun the Analysis Pipeline

The entire case study workflow is automated and reproducible. From the project root, execute:

```bash
# 1. Activate project environment
.venv\Scripts\activate   # On Windows
# source .venv/bin/activate  # On Linux/macOS

# 2. Collect latest live reviews from Google Play
python analysis/collect_reviews.py

# 3. Clean, deduplicate, and redact PII
python analysis/clean_reviews.py

# 4. Run NLP classification and issue tagging
python analysis/analyze_reviews.py

# 5. Generate updated chart assets
python analysis/generate_charts.py

# 6. Execute full verification test suite
pytest tests/test_analysis.py -v

# 7. Launch interactive Streamlit dashboard
streamlit run dashboard/app.py
```
