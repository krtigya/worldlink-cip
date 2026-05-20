#!/usr/bin/env python3
"""Seed database with ISPs and rules: python scripts/seed.py"""
import sys
sys.path.insert(0, ".")
from app.db.session import get_sync_db
from app.db.seed import seed_database
from app.logger import setup_logging

setup_logging()
session = next(get_sync_db())
seed_database(session)
session.close()
print("Seed complete.")
