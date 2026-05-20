#!/usr/bin/env python3
"""Run Alembic migrations: python scripts/migrate.py"""
import subprocess, sys
result = subprocess.run(["alembic", "upgrade", "head"], check=False)
sys.exit(result.returncode)
