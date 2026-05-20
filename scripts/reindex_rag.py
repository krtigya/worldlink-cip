#!/usr/bin/env python3
"""Re-index all plans into Qdrant: python scripts/reindex_rag.py"""
import sys
sys.path.insert(0, ".")
from app.db.session import get_sync_db
from app.rag.rag_service import RagService
from app.logger import setup_logging

setup_logging()
session = next(get_sync_db())
svc     = RagService()
count   = svc.index_all_plans(session)
print(f"Indexed {count} plans into Qdrant.")
