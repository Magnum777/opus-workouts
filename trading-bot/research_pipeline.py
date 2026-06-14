#!/usr/bin/env python3
"""
TradeBot Research Pipeline
Generates structured market research briefs using szzg007 framework
"""

import os
import sys
import json
from datetime import datetime, timezone

RESEARCH_DIR = os.path.join(os.path.dirname(__file__), "research")

def ensure_dir():
    os.makedirs(RESEARCH_DIR, exist_ok=True)

def get_report_path():
    """Get path for today's research report"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(RESEARCH_DIR, f"{today}.md")

def read_latest_report():
    """Read the most recent research report"""
    ensure_dir()
    try:
        files = sorted([f for f in os.listdir(RESEARCH_DIR) if f.endswith('.md')], reverse=True)
        if not files:
            return None
        with open(os.path.join(RESEARCH_DIR, files[0]), 'r') as f:
            return f.read()
    except:
        return None

def extract_scout_guidance(report_text):
    """Extract Scout Guidance section from a research report"""
    if not report_text:
        return None
    try:
        if "## Scout Guidance" in report_text:
            section = report_text.split("## Scout Guidance")[1].split("##")[0].strip()
            return section
        return None
    except:
        return None

def extract_risk_level(report_text):
    """Extract risk level from report"""
    if not report_text:
        return "unknown"
    try:
        for line in report_text.split('\n'):
            if "Risk level:" in line or "risk level:" in line:
                if "high" in line.lower():
                    return "high"
                elif "medium" in line.lower():
                    return "medium"
                elif "low" in line.lower():
                    return "low"
        return "unknown"
    except:
        return "unknown"

if __name__ == "__main__":
    # Quick test
    print(f"Research dir: {RESEARCH_DIR}")
    print(f"Today's report path: {get_report_path()}")
    latest = read_latest_report()
    if latest:
        print(f"Latest report found: {len(latest)} chars")
        guidance = extract_scout_guidance(latest)
        if guidance:
            print(f"\nScout Guidance:\n{guidance[:500]}...")
    else:
        print("No reports found")
