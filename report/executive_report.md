# MoveInSync Play Store Ratings & Customer Experience Optimization
## End-to-End Forward Deployed Engineering & Product Strategy Case Study

**Author:** Senior Forward Deployed Engineer & Product Analyst  
**Target Application:** MoveInSync (`com.moveinsync.ets`)  
**Assignment:** Forward Deployed Engineer (Intern to FTE) Evaluation  
**Dataset Grounding:** 2,139 Real Google Play Store Reviews (Scraped October 2026)  
**Deliverable Status:** Complete, Validated & Reproducible  

---

## 1. Executive Summary

MoveInSync provides mission-critical enterprise employee transportation solutions across global enterprises in India and emerging markets. Employees rely on the mobile app (`com.moveinsync.ets`) daily to schedule work commutes, track cabs, receive pickup notifications, verify safety escorts, and check into vehicles. 

A high-level inspection of Google Play displays a strong aggregate score of **4.64 / 5.0** across **114,878+ ratings**. However, a granular, evidence-based investigation into **2,139 written qualitative reviews** reveals a striking bimodal distribution: **48.1% of all written reviews are 1-star or 2-star ratings** (Sample Average: **2.94 / 5.0**). While silent users who experience normal commutes rarely leave reviews, employees facing commute disruptions experience severe distress and turn to the Play Store to vent.

The analysis identified five primary drivers of user dissatisfaction:
1. **Unskippable In-App Rating Gate (UX Backlash):** An unskippable, blocking modal demanding trip ratings after every ride directly drives frustrated users to retaliate on the Play Store with 1-star reviews (111+ direct mentions).
2. **Post-Update App Launch Crashes:** Update releases (e.g., `v12.19.x`) induce startup freeze loops and black screens, forcing repeated uninstalls/reinstalls (100+ reviews).
3. **Real-Time GPS Staleness & Lagging Telemetry:** Stationary or erratic vehicle markers prevent employees from knowing when to step outside (164 reviews).
4. **ETA Underestimation vs. Real Traffic:** MoveInSync ETAs frequently lag 20–30 minutes behind Google Maps, resulting in missed shifts and curb waiting (150 reviews).
5. **Booking Schedule Friction & Waitlist Ambiguity:** Employees are automatically dropped from rosters or placed on ambiguous waitlists without timely alerts (180 reviews).

To address these pain points, this case study delivers an actionable, evidence-based engineering plan prioritized by **Impact × Frequency × Confidence** (with safety adjustments), a **30/60/90-day roadmap**, an **interactive Streamlit telemetry dashboard**, and a concrete recommendation for **what the engineering team should execute on the next working day**.

---

## 2. Business Problem & Project Scope

### 2.1 The Strategic Problem
In an enterprise B2B2C model, MoveInSync contracts with enterprise employers (e.g., IT, BFSI, consulting firms), but the primary daily end-users are corporate employees. When employee commute applications fail:
- Employees miss time-sensitive client shifts or arrive fatigued.
- Enterprise client transport managers receive internal escalations, threatening multi-million-dollar contract renewals.
- Frustrated employees down-vote the app publicly on the Google Play Store, degrading brand reputation and creating friction during new client RFPs.

### 2.2 Scope Boundaries
- **In Scope:** MoveInSync employee-facing Android application (`com.moveinsync.ets`).
- **Out of Scope:** MoveInSync Driver partner application (`com.moveinsync.driver`), field operations portals, internal transport management web consoles.
- **Data Boundary:** All observations are strictly grounded in publicly accessible Google Play Store data without accessing private employee records or internal MoveInSync logs.

---

## 3. Research Methodology & Data Integrity

### 3.1 Data Acquisition
Data collection utilized `google-play-scraper` (v1.2.7) targeting `com.moveinsync.ets` with dual query passes:
- `Sort.NEWEST`: Captured recent 90–180 days to assess recent version stability (`v12.19.0`, updated October 8, 2026).
- `Sort.MOST_RELEVANT`: Captured historically upvoted, high-impact reviews across all star ratings.
- Collection executed on October 12, 2026, retrieving **2,139 unique, real user reviews** spanning September 2018 through October 2026.

### 3.2 Data Sanitization & PII Compliance
- **Deduplication:** Hash-indexed deduplication on `review_id` ensured zero duplicate records.
- **PII Scrubbing:** Reviewer usernames and avatar URLs were dropped. Regex masking scrubbed phone numbers (`[REDACTED_PHONE]`), emails (`[REDACTED_EMAIL]`), and employee/OTP IDs (`[REDACTED_ID]`).
- **Data Quality Audit:** 100% of star ratings strictly bound to $[1, 5]$; 100% of dates successfully parsed. Full audit logged in `data/data_quality_report.md`.

---

## 4. Current Public Rating Snapshot

| Metric | Official Play Store Telemetry | Analyzed Review Sample | Strategic Implication |
| :--- | :---: | :---: | :--- |
| **Star Rating** | **4.64 / 5.00** | **2.94 / 5.00** | Textual reviews represent a "friction funnel" |
| **Total Volume** | **114,878 Ratings** | **2,139 Written Reviews** | 98.1% of ratings are silent star taps |
| **Estimated Installs** | **3.2+ Million** | Full install footprint | Large enterprise scale |
| **Negative Share (1–2★)** | ~10–12% (Est. lifetime) | **48.11% (1,029 Reviews)** | Written reviews over-index on severe disruption |
| **Positive Share (4–5★)** | ~85–88% (Est. lifetime) | **45.54% (974 Reviews)** | Satisfied users leave concise praise |
| **Neutral Share (3★)** | ~3–4% | **6.36% (136 Reviews)** | Mixed feedback on recent redesigns |
| **Developer Responses** | N/A | **542 Replies (25.34%)** | 74.7% of reviews receive no public response |

> **Crucial Analytical Distinction:**  
> The Google Play aggregate rating (4.64★) represents lifetime, passive ratings often prompted during moments of user satisfaction. Conversely, the collected review dataset (2.94★ average) represents the voice of users driven to write detailed feedback by specific operational failures.

---

## 5. Key Findings with Grounded Metrics

The 2,139 reviewed records were processed through our multi-label NLP classification pipeline (`analysis/analyze_reviews.py`).

### Finding 1: Severe Bimodal Polarization (The U-Curve)
User ratings are heavily polarized: **41.00% are 1-star (877)** and **36.98% are 5-star (791)**. Middle ratings (2★, 3★, 4★) account for only 22.02% combined. MoveInSync either delivers an exceptional, seamless commute or experiences a catastrophic breakdown that completely derails an employee's morning.

### Finding 2: Unskippable Rating Prompt Directly Harms Public Ratings
**111 negative reviews (10.8% of negative volume)** explicitly call out the in-app trip feedback modal. Users report being trapped in a non-dismissible screen demanding a star rating before they can access their next booking. Frustrated by being forced to rate, users deliberately open Google Play to give 1 star.

### Finding 3: Post-Update Crash Loops Create Functional Deadlocks
**100 negative reviews (9.7%)** report app stability failures following recent updates. Users report white/black screens on cold launch, memory freezes, and forced uninstall/reinstall cycles. For employees trying to catch an early-morning cab, a crash is an immediate failure of service.

### Finding 4: The Commute Telemetry Gap (GPS Lag + ETA Underestimation)
**164 reviews cite GPS tracking staleness (15.9%)** and **150 reviews cite ETA miscalculations (14.6%)**. When cab locations freeze for 10 minutes, employees either rush outside prematurely in extreme weather or miss cabs that arrived unexpectedly. Employees frequently compare MoveInSync's ETA with Google Maps, noting that MoveInSync routinely under-predicts commute times by 20–40 minutes during peak congestion.

### Finding 5: Booking Ambiguity & Roster Locking
**180 reviews cite booking and scheduling friction (17.5%)**. Key grievances include opaque waitlisting (employees do not know if a seat is confirmed until 15 minutes prior), inflexible cut-off cancellation windows, and auto-cancellations that leave employees stranded without alternative corporate transport.

---

## 6. Representative Review Evidence

To bridge qualitative complaints with technical hypotheses, representative verbatim excerpts are documented below:

### Theme A: App Stability & Update Crashes
> **Review Date:** 2026-10-09 | ⭐ 1 Star | Version: `12.19.0`  
> *“whenever i update this app, i am not able to open the app again, I need to uninstall and reinstall again. facing this issue since 3 months”*  
> **What it suggests:** Corrupted shared preferences, failed local SQLite database migrations, or startup dependency crashes on app update.  
> **What it does not prove:** Which specific Android OEM flavors (e.g., MIUI, ColorOS, OneUI) or Android OS versions are affected.

### Theme B: Intrusive In-App Rating Gate
> **Review Date:** 2026-10-08 | ⭐ 1 Star | Version: `12.19.0`  
> *“forcing me to give rating after every ride, so I came here to give you 1 star. because if I don't rate, I can't use the app as there is no skip option.”*  
> **What it suggests:** A non-cancellable dialog blocking the primary activity view until a rating network call succeeds.  
> **What it does not prove:** The internal intent of the product team (likely aimed at internal driver scoring, but executed with blocking UX).

### Theme C: Routing, Detours & Pooling Inefficiencies
> **Review Date:** 2026-10-09 | ⭐ 1 Star | Version: `12.19.0`  
> *“MoveOutSync doesn't plan commutes; it plans cross-country pilgrimages. The ETA is an abstract joke where a 1-hour delay is considered punctual. The routing algorithm is pure genius: it clubs passengers from two different states into one cab at 8 AM, while empty cabs glide right past us. If you want a free Bharat Darshan tour before reaching office, this is it...”*  
> **What it suggests:** Suboptimal clustering heuristics in the dispatch algorithm, lacking constraints on maximum detour ratio or trip duration caps.  
> **What it does not prove:** Whether pooling constraints were dictated by employer cost-saving parameters rather than MoveInSync's algorithm alone.

### Theme D: GPS Staleness & Inaccurate Real-Time Tracking
> **Review Date:** 2026-10-08 | ⭐ 1 Star | Version: `12.19.0`  
> *“ETA calculator very bad. not sure on what basis its done. google maps always shows 3x the time shown in moveinsync app. tnis app just acts as a booking tool and no use of showing car location and eta.”*  
> **What it suggests:** Disconnect between static speed tables and live dynamic traffic routing APIs; driver app telemetry drops.  
> **What it does not prove:** Driver device connectivity status, GPS spoofing, or telecom network dead zones.

### Theme E: Promoter Strengths (To Be Preserved)
> **Review Date:** 2026-10-08 | ⭐ 5 Stars | Version: `12.19.0`  
> *“it's a great app for the night shift employees”*  
> **Review Date:** 2026-10-06 | ⭐ 5 Stars | Version: `12.18.0`  
> *“it's very convenient and I get all the details at the same time. Really helpful”*  
> **What it suggests:** Strong corporate value proposition in night-shift safety, female employee escort protocols, and consolidated vehicle info.

---

## 7. Evidence-Based Root-Cause Hypotheses

| Problem Domain | Observed User Symptom | Technical Root-Cause Hypotheses | Confidence Level | Internal Telemetry Needed to Verify | Proposed Engineering Fix | Metric to Confirm Improvement |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **App Stability** | App freezes on launch or crashes after updating; reinstall required. | 1. SQLite database migration error without fallback on app upgrade.<br>2. Corrupted Room/EncryptedSharedPreferences cache.<br>3. Fatal exception in cold-start DI graph. | **High** | Firebase Crashlytics stack traces, Android Vitals Cold-Start Crash Rate for v12.19.x. | Implement automated fallback schema rebuild with fallback data reset; add try-catch safe initialization. | Cold-start crash-free sessions > 99.5%; zero reinstall complaints. |
| **UX / Forced Rating** | Users forced to rate ride; cannot access booking features without rating. | 1. Modal dialog rendered with `isCancelable = false`.<br>2. App state machine blocks dashboard navigation until API post completes. | **High** | Rate prompt view count vs completion rate vs app forced exit events. | Convert rating dialog into a dismissible bottom sheet or non-blocking notification banner. | 90% reduction in negative reviews mentioning forced ratings; Play Store score recovery. |
| **GPS & Tracking** | Vehicle icon stays frozen for 10–15 mins, then teleports; ETA doesn't update. | 1. Aggressive battery optimization on OEM driver devices killing background MQTT socket.<br>2. Driver app location service throttling.<br>3. Backpressure on backend telemetry ingestion queue. | **High** | Driver ping latency, MQTT connection drop rate, GPS telemetry timestamp lag (`now() - ping_ts`). | Implement persistent Foreground Service on driver app; dead-reckoning map interpolation; visible "Stale Telemetry" warning. | P95 GPS staleness latency < 15 seconds; tracking complaints down 60%. |
| **ETA Calibration** | MoveInSync ETA differs by 20–40 mins from Google Maps in peak traffic. | 1. Static road speed tables used during dispatch.<br>2. Failure to ingest live road congestion APIs.<br>3. Inadequate buffer for multi-stop boarding delays. | **Medium** | Mean Absolute Error (MAE) between Predicted ETA and Actual Arrival Timestamp across shift hours. | Integrate live traffic routing API (Google Maps / Mapbox Matrix API); apply dynamic time-of-day congestion weights. | ETA prediction MAE < 5 minutes in urban peak hours. |
| **Booking & Roster** | Cabs cancelled with zero notice; waitlist status ambiguous until too late. | 1. Batch rostering runs fail to confirm edge-case routes.<br>2. Silent drop of overflow employees without push alert fallback. | **Medium** | Shift roster unassigned rate, waitlist conversion rate, push notification delivery receipts. | Real-time waitlist queue position display (e.g., "Waitlist #3"); proactive auto-notification 2 hrs prior to shift. | Unscheduled drop complaints down 50%; booking support tickets -40%. |
| **Driver & Safety** | Rash driving, unverified late-night drivers, missing security escorts. | 1. Fleet telematics not enforcing speed limits in real time.<br>2. Manual escort check-in bypassed by drivers. | **High** | OBD-II accelerometer alerts, SOS button activations, escort QR verification audit logs. | Automated real-time speeding alerts to transport desk; mandatory two-factor QR scan for security escorts before cab dispatch. | Zero unverified late-night escort trips; driver safety escalations -75%. |

---

## 8. Prioritized Recommendation Matrix

Prioritization is calculated using the standard framework:
$$\text{Priority Score} = (\text{Impact} \times \text{Frequency} \times \text{Confidence}) + \text{Safety Severity Adjustment}$$
- **Impact (1–10):** User satisfaction and business retention value.
- **Frequency (1–10):** Normalized review prevalence (based on actual review counts).
- **Confidence (1–10):** Certainty of technical hypothesis.
- **Safety Adjustment (+25 to +50):** Applied to life-safety and security defects to guarantee P0 status regardless of frequency.

| Priority | Problem Addressed | Review Evidence | Proposed Implementation | Impact (1–10) | Effort (1–10) | Confidence (1–10) | Responsible Team | Success Target | Validation Method |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **P0** | **Post-Update App Launch Crash Loop** | 100 reviews; 9.7% of negative sample | Implement graceful SQLite migration fallback; wrap cold-start DI in resilient exception handler; purge corrupted cache. | 9.5 | 3.0 (2 wks) | 9.5 | Mobile Android Eng | Crash-free sessions > 99.5% | Staged rollouts (5% -> 20% -> 100%) monitoring Firebase Crashlytics. |
| **P0** | **Unskippable Post-Ride Rating Gate** | 111 reviews; 10.8% of negative sample | Decouple rating modal; replace with dismissible bottom card; enforce Google Play In-App Review guidelines. | 9.0 | 1.5 (3 days) | 10.0 | Product / UX Eng | Zero "forced rating" reviews; store rating trend reversal | A/B test modal vs non-blocking card; monitor rating completion vs Play Store sentiment. |
| **P0** | **Driver Rash Driving & Late-Night Safety** | 28 reviews; safety-critical escalations | Enforce real-time speed governor alerts via telematics; mandatory two-way QR escort verification for female night shifts. | 9.8 | 4.5 (3 wks) | 9.0 | Transport Ops / IoT Eng | 100% verified escort trips; speed violations down 80% | Bi-weekly safety desk compliance audits; automated OBD-II incident reports. |
| **P1** | **GPS Stale Vehicle Telemetry** | 164 reviews; 15.9% of negative sample | Maintain persistent Foreground Service on driver app; add dead-reckoning interpolation; display "Last seen X sec ago". | 8.5 | 6.5 (4 wks) | 8.5 | Mobile & Backend Telemetry | P95 telemetry latency < 15s | Field drive tests with dual GPS logger comparing live app marker vs physical location. |
| **P1** | **ETA Underestimation vs Real Traffic** | 150 reviews; 14.6% of negative sample | Integrate live traffic matrix APIs; incorporate multi-passenger boarding time buffers (3 mins per stop). | 8.2 | 6.0 (4 wks) | 8.0 | Routing / Data Science | ETA MAE < 5 mins | Compare dispatch ETA with actual timestamp across 50,000 corporate trips. |
| **P1** | **Waitlist Ambiguity & Roster Locking** | 180 reviews; 17.5% of negative sample | Show real-time waitlist queue position; send automated fallback SMS/push 2 hrs prior to pickup cutoff. | 8.0 | 4.0 (3 wks) | 8.5 | Product Eng | Booking cancellation disputes down 50% | Track employee booking confirmation SLA and helpdesk ticket volume. |
| **P1** | **Seatbelt Modal Blocking Boarding OTP** | 108 reviews; 10.5% of negative sample | Decouple safety awareness modal from boarding OTP display; render OTP prominently on persistent home card. | 7.5 | 2.5 (1 wk) | 9.0 | Mobile Eng | Boarding delay at curb < 15 seconds | Curbside boarding audit; OTP generation error logs. |
| **P2** | **SSO Token Refresh & Auth Friction** | 108 reviews; 10.5% of negative sample | Silent background token refresh; graceful OAuth fallback; offline PIN caching for boarding. | 7.0 | 3.5 (2 wks) | 8.0 | Enterprise Auth Eng | Auth failure rate < 0.2% | Synthetic login tests across Okta, Azure AD, Ping Identity connectors. |
| **P2** | **Extreme Pooling Detours** | 129 reviews; 12.5% of negative sample | Introduce strict maximum detour constraint (max travel time <= 1.4x direct point-to-point duration). | 7.2 | 7.5 (6 wks) | 7.5 | Operations Research | P95 commute duration -20% | Fleet simulation comparing current clustering vs constrained routing algorithm. |
| **P2** | **Unresponsive Helpdesk Escalation** | 85 reviews; 8.3% of negative sample | In-app 1-click live chat with automated transport desk routing; dedicated emergency escalation dialer. | 6.8 | 5.0 (3 wks) | 8.5 | Customer Support Ops | First response time < 3 mins | Helpdesk Zendesk/Freshdesk SLA dashboard. |

---

## 9. 30 / 60 / 90-Day Execution Roadmap

```
Phase 1: Days 1–30 (Critical Defect Hotfixes & Safety Compliance)
├── [Week 1] Release v12.19.1 hotfix: Remove blocking post-ride rating modal (Immediate Quick Win).
├── [Week 2] Fix SQLite database migration crash in cold startup; purge corrupted local preferences.
├── [Week 3] Audit driver night-shift escort compliance; lock dispatch for unverified escort trips.
└── [Week 4] Deploy internal Play Store review ingestion pipeline & telemetry alert monitor.

Phase 2: Days 31–60 (Core Commute Real-Time Reliability)
├── [Week 5–6] Refactor driver app background location service; implement MQTT socket keep-alive.
├── [Week 7] Decouple boarding OTP display from secondary seatbelt advisory dialogs.
├── [Week 8] Roll out live traffic ETA engine with multi-stop pickup buffers in top 3 metros.
└── [Week 8] A/B test waitlist queue transparency UI on employee rostering view.

Phase 3: Days 61–90 (Algorithm Optimization, Support & Enterprise Scalability)
├── [Week 9–10] Implement hard detour time caps (max 1.4x direct route) in dispatch clustering.
├── [Week 11] Embed real-time in-app helpdesk live chat with automated cab re-dispatch.
└── [Week 12] Standardize automated bi-weekly Play Store CX intelligence reports for leadership.
```

---

## 10. Repeatable Rating-Monitoring & CX Telemetry System

To ensure that Play Store ratings are systematically monitored over time, MoveInSync should establish a permanent, automated feedback tracking mechanism that couples public app store signals with internal operational metrics.

### 10.1 Monitoring Telemetry Architecture

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     PUBLIC STORE TELEMETRY      │       │   INTERNAL OPERATIONAL METRICS  │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ • Daily New Review Volume       │       │ • Crash-Free Users (Crashlytics)│
│ • Weekly 1-2★ Negative Share    │  ◄──► │ • P95 Driver GPS Ping Latency   │
│ • Net Sentiment Polarity Index  │       │ • ETA Prediction MAE vs Actual  │
│ • Issue Category Tag Frequencies│       │ • Unassigned Roster Rate        │
│ • Developer Response Latency    │       │ • Escort Verification Rate (SOS)│
└─────────────────────────────────┘       └─────────────────────────────────┘
                 ▲                                         ▲
                 └────────────────────┬────────────────────┘
                                      │
                         ┌────────────────────────┐
                         │ AUTOMATED CX DASHBOARD │
                         │ (Daily Streamlit Sync) │
                         └────────────────────────┘
```

### 10.2 KPI Definition & Measurement Framework

| Metric Category | Specific KPI | Definition & Calculation | Data Source | Frequency | Target / Benchmark |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Public Store** | **Written Negative Share** | $\frac{\text{Count}(1\star + 2\star)}{\text{Total Written Reviews}} \times 100$ | Google Play Scraper | Daily | Baseline: 48.1% $\rightarrow$ **Target: < 25.0%** |
| **Public Store** | **Issue Specific Defect Ratio** | Negative reviews per category / Total Negative | Google Play Scraper | Weekly | Prompt complaints: **< 1%**; Crashes: **< 3%** |
| **Public Store** | **Developer Reply Turnaround** | Median hours from review publication to reply | Google Play Scraper | Daily | Baseline: 4.3 days $\rightarrow$ **Target: < 24 hours** |
| **Internal Eng** | **Crash-Free Session Rate** | Crash-free user sessions / Total sessions | Firebase Crashlytics | Real-Time | **Target: > 99.8%** |
| **Internal IoT** | **GPS Telemetry Staleness** | P95 $(\text{Current Time} - \text{Driver Last Ping})$ | MQTT Broker Telemetry | Real-Time | **Target: < 15 seconds** |
| **Internal Data** | **ETA Prediction MAE** | Mean absolute error between Predicted ETA & Drop | Route Engine Logs | Daily | **Target: < 5 minutes** |
| **Internal Ops** | **Safety Escort Audit** | Verified escort scans / Total required night trips | Transport Operations | Daily | **Target: Strictly 100.0%** |

> **Ethical Review Policy Notice:**  
> In compliance with Google Play Store Developer Content Policies, ratings must never be artificially inflated through incentives or filtered gates. The only sustainable path to a 4.8★ app rating is eliminating functional commute failures. In-app rating prompts must use the official Google Play In-App Review API at moments of genuine user delight (e.g., after 5 consecutive on-time trips).

---

## 11. Risks, Assumptions & Data Limitations

### 11.1 Methodological Assumptions
- **Sample Representativeness:** We assume that while written reviews over-index on negative experiences, the relative proportion between issue categories (e.g., GPS vs. Crashes vs. Booking) accurately reflects the real-world severity distribution across the user base.
- **Effort Estimations:** Engineering effort scores (1–10) are preliminary engineering assumptions based on typical Android/Spring Boot architectures and require formal sprint estimation by MoveInSync tech leads.

### 11.2 Public Data Limitations
- **No Direct Stack Traces:** Public reviews confirm *that* the app crashes after an update, but cannot pinpoint the exact class or line number without internal Crashlytics access.
- **Enterprise Policy Masking:** A cancelled cab or locked roster may be caused by an employer's transport budget constraint rather than a software defect. Internal client tenant configurations are required to isolate software bugs from client policy rules.

---

## 12. Final Recommendation: Day-One Action Plan

### What MoveInSync Should Fix First Tomorrow

If MoveInSync’s product and engineering team could start fixing only **three things tomorrow**, they should execute the following high-leverage initiatives:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DAY-ONE ENGINEERING TRIAGE PLAN                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. KILL THE UNBLOCKABLE TRIP RATING MODAL (UX Hotfix — 3 Days)              │
│    • Why: It directly triggers 10.8% of all 1-star reviews. Users are       │
│      deliberately going to the Play Store to vent because they are trapped  │
│      by an unskippable in-app prompt. Removing the block stops the bleed    │
│      immediately with almost zero engineering risk.                         │
│    • How to Measure: Monitor daily 1-star review intake; verify keyword     │
│      mentions of "forcing rating" drop to zero within 14 days.              │
│                                                                             │
│ 2. RESOLVE THE POST-UPDATE COLD-START CRASH LOOP (Mobile Eng — 1 Sprint)    │
│    • Why: 9.7% of negative reviews report that the latest update cannot     │
│      open or crashes on launch, forcing painful reinstall loops for daily   │
│      office commuters.                                                      │
│    • How to Measure: Crash-Free User Sessions in Firebase Crashlytics       │
│      rising above 99.5%; elimination of "won't open after update" reviews.  │
│                                                                             │
│ 3. DEPLOY TELEMETRY STALENESS ALERTS & DRIVER KEEPALIVE (IoT/Eng — 2 Weeks) │
│    • Why: 15.9% of complaints stem from frozen vehicle markers and stale    │
│      ETAs. If employees cannot trust cab locations, the app fails its       │
│      primary functional utility.                                            │
│    • How to Measure: P95 GPS telemetry delay drops under 15 seconds; curbside│
│      no-show and driver delay escalations decrease by 40%.                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Case Study Deliverables Index

All code, datasets, visualization outputs, and testing scripts are located in the project workspace:
- **Executive Report:** [`report/executive_report.md`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/report/executive_report.md)
- **Methodology & Tools:** [`report/methodology_and_tools.md`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/report/methodology_and_tools.md)
- **App Metadata Snapshot:** [`report/source_log.csv`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/report/source_log.csv)
- **Raw Public Reviews:** [`data/raw_reviews.csv`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/data/raw_reviews.csv)
- **Cleaned Reviews:** [`data/cleaned_reviews.csv`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/data/cleaned_reviews.csv)
- **Analyzed Review Dataset:** [`data/review_analysis.csv`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/data/review_analysis.csv)
- **Data Quality Report:** [`data/data_quality_report.md`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/data/data_quality_report.md)
- **Review Scraper:** [`analysis/collect_reviews.py`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/analysis/collect_reviews.py)
- **Sanitizer Pipeline:** [`analysis/clean_reviews.py`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/analysis/clean_reviews.py)
- **NLP Classifier:** [`analysis/analyze_reviews.py`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/analysis/analyze_reviews.py)
- **Chart Generator:** [`analysis/generate_charts.py`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/analysis/generate_charts.py)
- **Interactive Dashboard:** [`dashboard/app.py`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/dashboard/app.py)
- **Verification Tests:** [`tests/test_analysis.py`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/tests/test_analysis.py)
- **Charts:**
  - [`outputs/rating_distribution.png`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/outputs/rating_distribution.png)
  - [`outputs/rating_trend.png`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/outputs/rating_trend.png)
  - [`outputs/issue_frequency.png`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/outputs/issue_frequency.png)
  - [`outputs/priority_matrix.png`](file:///c:/Users/Shahn/Desktop/MoveInSync_Case_Study/outputs/priority_matrix.png)
