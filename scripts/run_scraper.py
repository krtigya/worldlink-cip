#!/usr/bin/env python3
"""Manually trigger scrape for all ISPs: python scripts/run_scraper.py"""
import sys
sys.path.insert(0, ".")
from app.ingestion.tasks.scrape_tasks import scrape_all_isps
from app.logger import setup_logging

setup_logging()
result = scrape_all_isps()
print(f"Queued {result['queued']} scrape jobs.")
