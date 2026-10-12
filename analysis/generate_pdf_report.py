"""
Module: generate_pdf_report.py
Purpose: Compiles the executive case study into a publication-grade PDF report (report/executive_report.pdf)
         using ReportLab with styling, tables, callouts, and embedded charts.
"""

import os
import sys
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..")) if os.path.basename(CURRENT_DIR) == "analysis" else os.path.abspath(".")

PDF_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "report", "executive_report.pdf")
RATING_DIST_IMG = os.path.join(PROJECT_ROOT, "outputs", "rating_distribution.png")
ISSUE_FREQ_IMG = os.path.join(PROJECT_ROOT, "outputs", "issue_frequency.png")
PRIORITY_MATRIX_IMG = os.path.join(PROJECT_ROOT, "outputs", "priority_matrix.png")

def create_pdf_report():
    print(f"[*] Generating PDF report at {PDF_OUTPUT_PATH}...")
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A237E"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#D84315"),
        spaceAfter=14
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#546E7A"),
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        "H1Style",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0D47A1"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "H2Style",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#263238"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#212121"),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    callout_style = ParagraphStyle(
        "CalloutStyle",
        parent=body_style,
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1A237E")
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#212121")
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title Banner
    story.append(Paragraph("MoveInSync Play Store Ratings & CX Strategy", title_style))
    story.append(Paragraph("End-to-End Forward Deployed Engineering & Product Analysis Case Study", subtitle_style))
    story.append(Paragraph("<b>Target App:</b> MoveInSync (<code>com.moveinsync.ets</code>) | <b>Evaluator Role:</b> Senior FDE / Product Analyst | <b>Date:</b> October 2026", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1565C0"), spaceAfter=12))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "MoveInSync provides mission-critical enterprise employee transportation solutions. While Google Play displays an official aggregate score of <b>4.64 / 5.0</b> across <b>114,878+ lifetime ratings</b>, an evidence-based audit of <b>2,139 written reviews</b> reveals severe friction: <b>48.1% of written reviews are 1-star or 2-star ratings</b> (sample average: <b>2.94 / 5.0</b>). Silent users who experience ordinary rides rarely write reviews; employees facing commute disruptions write detailed, negative feedback. This case study diagnoses root causes, prioritizes high-impact technical fixes, and outlines a 30/60/90-day roadmap.",
        body_style
    ))

    # Callout Box
    callout_data = [[
        Paragraph("<b>Key Findings Summary:</b><br/>"
                  "• <b>Bimodal U-Curve:</b> 41.0% are 1★, 37.0% are 5★; users experience either total delight or total failure.<br/>"
                  "• <b>UX Friction:</b> 111 reviews cite an unskippable post-trip rating popup as the direct reason they left a 1★ Play Store rating.<br/>"
                  "• <b>Stability:</b> 100 reviews report app crash loops and white screens following recent v12.19.x updates.<br/>"
                  "• <b>Telemetry Lag:</b> 164 reviews cite stale GPS markers and 150 cite severe ETA underestimations.", callout_style)
    ]]
    callout_table = Table(callout_data, colWidths=[7.2 * inch])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E8EAF6")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3F51B5")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))

    # 2. Rating Snapshot Table
    story.append(Paragraph("2. Official Telemetry vs. Written Review Sample", h1_style))
    metrics_data = [
        [Paragraph("Metric", table_header), Paragraph("Official Play Store", table_header), Paragraph("Collected Sample", table_header), Paragraph("Implication", table_header)],
        [Paragraph("Overall Score", table_cell), Paragraph("<b>4.64 / 5.00</b>", table_cell), Paragraph("<b>2.94 / 5.00</b>", table_cell), Paragraph("Written reviews act as an escalation funnel", table_cell)],
        [Paragraph("Total Volume", table_cell), Paragraph("114,878 Ratings", table_cell), Paragraph("2,139 Written Reviews", table_cell), Paragraph("98.1% of all ratings are passive/silent", table_cell)],
        [Paragraph("Negative Share (1–2★)", table_cell), Paragraph("~10–12% (Est.)", table_cell), Paragraph("<b>48.11% (1,029)</b>", table_cell), Paragraph("Dissatisfaction strongly over-indexes in text", table_cell)],
        [Paragraph("Positive Share (4–5★)", table_cell), Paragraph("~85–88% (Est.)", table_cell), Paragraph("<b>45.54% (974)</b>", table_cell), Paragraph("Promoters leave concise praise", table_cell)],
        [Paragraph("Dev Reply Coverage", table_cell), Paragraph("N/A", table_cell), Paragraph("25.34% (542 replies)", table_cell), Paragraph("Median reply delay: 4.3 days", table_cell)]
    ]
    t_metrics = Table(metrics_data, colWidths=[1.6 * inch, 1.6 * inch, 1.8 * inch, 2.2 * inch])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 12))

    # Embedded Distribution Chart
    if os.path.exists(RATING_DIST_IMG):
        story.append(Image(RATING_DIST_IMG, width=6.8 * inch, height=3.6 * inch))
        story.append(Spacer(1, 10))

    # 3. Top Recurring Problems
    story.append(Paragraph("3. Top Recurring Pain Points in Negative Reviews (N=1,029)", h1_style))
    story.append(Paragraph("Multi-label issue frequencies among 1-star and 2-star reviews:", body_style))
    
    issues_table_data = [
        [Paragraph("Issue Domain", table_header), Paragraph("Negative Mentions", table_header), Paragraph("% of Negative", table_header), Paragraph("Primary Technical Symptom", table_header)],
        [Paragraph("Booking & Scheduling", table_cell), Paragraph("180", table_cell), Paragraph("17.5%", table_cell), Paragraph("Waitlist ambiguity; unexpected auto-cancellations", table_cell)],
        [Paragraph("GPS & Live Tracking", table_cell), Paragraph("164", table_cell), Paragraph("15.9%", table_cell), Paragraph("Frozen vehicle marker; jumpy vehicle coordinates", table_cell)],
        [Paragraph("ETA & Timing Accuracy", table_cell), Paragraph("150", table_cell), Paragraph("14.6%", table_cell), Paragraph("ETA underestimates peak traffic by 20–40 mins", table_cell)],
        [Paragraph("Routing & Detours", table_cell), Paragraph("129", table_cell), Paragraph("12.5%", table_cell), Paragraph("Inefficient multi-stop clubbing; excessive commute times", table_cell)],
        [Paragraph("UI/UX & Forced Rating", table_cell), Paragraph("111", table_cell), Paragraph("10.8%", table_cell), Paragraph("Unskippable post-ride rating popup forces Play Store 1★", table_cell)],
        [Paragraph("OTP & Boarding", table_cell), Paragraph("108", table_cell), Paragraph("10.5%", table_cell), Paragraph("Seatbelt popup obscures OTP; QR scan failures", table_cell)],
        [Paragraph("Login & SSO Auth", table_cell), Paragraph("108", table_cell), Paragraph("10.5%", table_cell), Paragraph("Repeated logout; login OTP delays; token expiration", table_cell)],
        [Paragraph("App Stability & Crashes", table_cell), Paragraph("100", table_cell), Paragraph("9.7%", table_cell), Paragraph("Cold-start launch crash; white screen after update", table_cell)],
        [Paragraph("Driver Conduct & Safety", table_cell), Paragraph("28", table_cell), Paragraph("2.7%", table_cell), Paragraph("Rash driving; unverified night-shift escort absence", table_cell)]
    ]
    t_issues = Table(issues_table_data, colWidths=[1.8 * inch, 1.2 * inch, 1.2 * inch, 3.0 * inch])
    t_issues.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C62828")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_issues)
    story.append(Spacer(1, 12))

    # Embedded Issue Frequency Chart
    if os.path.exists(ISSUE_FREQ_IMG):
        story.append(Image(ISSUE_FREQ_IMG, width=6.8 * inch, height=3.8 * inch))
        story.append(Spacer(1, 10))

    # 4. Prioritization Matrix & Recommendations
    story.append(Paragraph("4. Prioritized Recommendations & Action Matrix", h1_style))
    story.append(Paragraph("Prioritization follows Impact x Frequency x Confidence with a safety override:", body_style))

    prio_data = [
        [Paragraph("Prio", table_header), Paragraph("Initiative", table_header), Paragraph("Impact", table_header), Paragraph("Effort", table_header), Paragraph("Team", table_header), Paragraph("Success Target", table_header)],
        [Paragraph("<b>P0</b>", table_cell), Paragraph("Remove Blocking Trip Rating Modal", table_cell), Paragraph("9.0", table_cell), Paragraph("1.5 (3 days)", table_cell), Paragraph("Product/UX", table_cell), Paragraph("Forced rating reviews -> 0", table_cell)],
        [Paragraph("<b>P0</b>", table_cell), Paragraph("Fix Post-Update Cold-Start Crash Loop", table_cell), Paragraph("9.5", table_cell), Paragraph("3.0 (2 wks)", table_cell), Paragraph("Mobile Eng", table_cell), Paragraph("Crash-free sessions > 99.5%", table_cell)],
        [Paragraph("<b>P0</b>", table_cell), Paragraph("Driver Rash Driving & Escort Telematics", table_cell), Paragraph("9.8", table_cell), Paragraph("4.5 (3 wks)", table_cell), Paragraph("Ops / IoT", table_cell), Paragraph("100% verified night escorts", table_cell)],
        [Paragraph("<b>P1</b>", table_cell), Paragraph("Real-Time GPS Staleness & Keepalive", table_cell), Paragraph("8.5", table_cell), Paragraph("6.5 (4 wks)", table_cell), Paragraph("Mobile/IoT", table_cell), Paragraph("P95 telemetry latency < 15s", table_cell)],
        [Paragraph("<b>P1</b>", table_cell), Paragraph("Dynamic ETA Calibration vs Traffic", table_cell), Paragraph("8.2", table_cell), Paragraph("6.0 (4 wks)", table_cell), Paragraph("Data Science", table_cell), Paragraph("ETA MAE < 5 mins in peak hours", table_cell)],
        [Paragraph("<b>P1</b>", table_cell), Paragraph("Waitlist Transparency UI & Early Alerts", table_cell), Paragraph("8.0", table_cell), Paragraph("4.0 (3 wks)", table_cell), Paragraph("Product Eng", table_cell), Paragraph("Booking support tickets -40%", table_cell)],
        [Paragraph("<b>P1</b>", table_cell), Paragraph("Decouple Seatbelt Modal from OTP", table_cell), Paragraph("7.5", table_cell), Paragraph("2.5 (1 wk)", table_cell), Paragraph("Mobile Eng", table_cell), Paragraph("Boarding curb delay < 15s", table_cell)],
        [Paragraph("<b>P2</b>", table_cell), Paragraph("SSO Silent Token Background Refresh", table_cell), Paragraph("7.0", table_cell), Paragraph("3.5 (2 wks)", table_cell), Paragraph("Security Eng", table_cell), Paragraph("Auth failure rate < 0.2%", table_cell)],
        [Paragraph("<b>P2</b>", table_cell), Paragraph("Strict Pooling Detour Cap (<= 1.4x)", table_cell), Paragraph("7.2", table_cell), Paragraph("7.5 (6 wks)", table_cell), Paragraph("Routing Alg", table_cell), Paragraph("P95 commute time -20%", table_cell)],
        [Paragraph("<b>P2</b>", table_cell), Paragraph("In-App Transport Desk Priority Live Chat", table_cell), Paragraph("6.8", table_cell), Paragraph("5.0 (3 wks)", table_cell), Paragraph("Support Ops", table_cell), Paragraph("First response SLA < 3 mins", table_cell)]
    ]
    t_prio = Table(prio_data, colWidths=[0.6 * inch, 2.3 * inch, 0.7 * inch, 1.0 * inch, 1.1 * inch, 1.5 * inch])
    t_prio.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0D47A1")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_prio)
    story.append(Spacer(1, 12))

    # Embedded Priority Matrix Chart
    if os.path.exists(PRIORITY_MATRIX_IMG):
        story.append(Image(PRIORITY_MATRIX_IMG, width=6.8 * inch, height=4.2 * inch))
        story.append(Spacer(1, 10))

    # 5. Day-One Action Plan
    story.append(Paragraph("5. Day-One Action Plan: What to Fix Tomorrow", h1_style))
    story.append(Paragraph(
        "<b>Question:</b> <i>'If MoveInSync's product and engineering team could start fixing only three things tomorrow, what should they fix first, why, and how would we measure whether the fixes worked?'</i>",
        body_style
    ))
    
    day_one_text = (
        "<b>1. Kill the Unskippable In-App Trip Rating Modal (UX Hotfix — 3 Days)</b><br/>"
        "• <i>Why:</i> 111 reviews (10.8% of negative reviews) prove this dialog actively drives users to the Play Store to vent. It is an artificial, self-inflicted negative rating driver.<br/>"
        "• <i>How to Measure:</i> Daily negative reviews citing forced ratings drop to 0 within 14 days.<br/><br/>"
        "<b>2. Resolve Post-Update Startup Crash Loop (Mobile Eng — 1 Sprint)</b><br/>"
        "• <i>Why:</i> 100 reviews report that updating the app leaves it unusable on launch, breaking employee morning commutes and forcing repeated re-installs.<br/>"
        "• <i>How to Measure:</i> Crashlytics crash-free session rate > 99.5%; elimination of 'won't open' reviews.<br/><br/>"
        "<b>3. Enforce Driver GPS Keep-Alive & Telemetry Staleness Alerts (IoT/Eng — 2 Weeks)</b><br/>"
        "• <i>Why:</i> 164 reviews cite frozen markers and inaccurate ETAs. If employees cannot trust real-time cab locations, the app fails its primary functional utility.<br/>"
        "• <i>How to Measure:</i> P95 GPS staleness latency drops under 15 seconds; curbside driver delay complaints decrease by 40%."
    )
    t_dayone = Table([[Paragraph(day_one_text, body_style)]], colWidths=[7.2 * inch])
    t_dayone.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFF8E1")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#FFA000")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_dayone)
    story.append(Spacer(1, 14))

    # Build document
    doc.build(story)
    print(f"[+] Successfully compiled PDF to {PDF_OUTPUT_PATH} ({os.path.getsize(PDF_OUTPUT_PATH):,} bytes)")

if __name__ == "__main__":
    create_pdf_report()
