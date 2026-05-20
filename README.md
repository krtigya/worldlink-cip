# WorldLink CIP — Python Edition
## Competitive Intelligence Platform

Internal system to track competitor ISPs (Vianet, Subisu, DishHome, CG Net)
and generate actionable insights for WorldLink Communications.

---

## Tech Stack

| Layer         | Technology                            |
|---------------|---------------------------------------|
| API           | FastAPI + Uvicorn                     |
| Scraping      | Playwright (Python)                   |
| Task Queue    | Celery + Redis (BullMQ equivalent)    |
| Database      | PostgreSQL 15 + SQLAlchemy 2.0        |
| Migrations    | Alembic                               |
| Vector DB     | Qdrant                                |
| Embeddings    | sentence-transformers (local, free)   |
| LLM           | Groq (llama-3.1-8b-instant, free)     |
| Alerts        | Slack Webhooks + Email (Jinja2 HTML)  |
| Validation    | Pydantic v2                           |
| Logging       | structlog                             |

---

## Quick Start

```bash
# 1. Clone and setup
cp .env.example .env
# Edit .env — add your GROQ_API_KEY and SLACK_WEBHOOK_URL

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Start infrastructure
docker-compose up -d postgres redis qdrant

# 6. Run migrations
alembic upgrade head

# 7. Seed ISPs and rules
python scripts/seed.py

# 8. Start API server
uvicorn app.main:app --reload --port 8000

# 9. Start Celery worker (separate terminal)
celery -A app.ingestion.tasks.celery_app worker --loglevel=info -Q scrape,reports -c 3

# 10. Start Celery beat scheduler (separate terminal)
celery -A app.ingestion.tasks.celery_app beat --loglevel=info
```

---

## API Endpoints

| Method | Path                      | Description                              |
|--------|---------------------------|------------------------------------------|
| GET    | /health                   | Health check                             |
| GET    | /api/isps                 | List all ISPs                            |
| GET    | /api/plans                | List plans (filter: isp, speed, price)   |
| GET    | /api/plans/compare        | WorldLink vs competitors                 |
| GET    | /api/plans/{id}/history   | Pricing history for a plan               |
| GET    | /api/changes              | Change log (filter: severity, type, isp) |
| GET    | /api/changes/summary      | Change counts by type this week          |
| POST   | /api/rag/query            | Semantic plan search                     |
| POST   | /api/rag/ask              | Natural language Q&A (full RAG)          |
| POST   | /api/rag/reindex          | Re-index all plans in Qdrant             |
| GET    | /api/reports/latest       | Latest weekly report                     |
| POST   | /api/reports/generate     | Generate report on-demand                |
| POST   | /api/scrape/trigger       | Trigger manual scrape                    |
| GET    | /api/scrape/runs          | Scrape run history                       |
| GET    | /docs                     | Interactive Swagger UI                   |

---

## Example RAG Queries

```bash
# Semantic search
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"q": "cheapest 300 Mbps plan", "max_price": 2000}'

# Natural language question
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which ISP offers best value fiber plan with Netflix under NPR 2500?"}'
```

---

## Project Structure

```
cip-python/
├── app/
│   ├── main.py                    # FastAPI app factory + lifespan
│   ├── config.py                  # Pydantic settings
│   ├── logger.py                  # structlog setup
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── isp.py
│   │   ├── plan.py
│   │   ├── pricing_history.py
│   │   ├── campaign.py
│   │   ├── change_log.py
│   │   ├── scrape_run.py
│   │   ├── weekly_report.py
│   │   └── intel_rule.py
│   ├── db/
│   │   ├── session.py             # Async + sync SQLAlchemy sessions
│   │   └── seed.py                # ISP + rules seeding
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── ingestion/
│   │   ├── scrapers/
│   │   │   ├── base_scraper.py    # Playwright base + config-driven
│   │   │   ├── vianet_scraper.py  # XHR-intercept scraper
│   │   │   └── scraper_factory.py
│   │   └── tasks/
│   │       ├── celery_app.py      # Celery + beat schedule
│   │       └── scrape_tasks.py    # Celery task definitions
│   ├── normalization/
│   │   └── normalizer.py          # Speed/price/bundle normalization
│   ├── detection/
│   │   └── change_detector.py     # Field-level diff engine
│   ├── intelligence/
│   │   └── rules_engine.py        # Configurable alert rules
│   ├── rag/
│   │   └── rag_service.py         # Qdrant + sentence-transformers + Groq
│   ├── reports/
│   │   └── report_generator.py    # Weekly report + LLM summarization
│   ├── alerts/
│   │   └── alert_dispatcher.py    # Slack + Email dispatcher
│   └── api/
│       ├── routes/                # FastAPI routers
│       └── middleware/            # Request logging
├── alembic/                       # Database migrations
├── tests/                         # Pytest test suite
├── scripts/                       # CLI utility scripts
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Cron Schedule (Celery Beat)

| Job              | Schedule        | Description                        |
|------------------|-----------------|------------------------------------|
| Scrape all ISPs  | Every 6 hours   | Full scrape + change detection     |
| Weekly report    | Monday 8am NPT  | Generate & persist weekly report   |

---

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_normalizer.py -v      # normalizer unit tests
pytest tests/test_change_detector.py -v # detector unit tests
```

---

## Monitor Celery Jobs

Open Flower dashboard at: http://localhost:5555
