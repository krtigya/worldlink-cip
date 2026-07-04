                        WorldLink CIP — Competitive Intelligence Platform

A system that automatically tracks internet service provider (ISP) pricing in Nepal, detects when competitors change their plans, sends alerts, and displays everything on a live dashboard.
What This Project Does
WorldLink is an ISP in Nepal. This platform watches competitor ISPs (Vianet, DishHome, and CGNet) every 6 hours, compares their plans against WorldLink's plans, and immediately notifies the team when anything changes — a price drop, a new plan, a bundle addition, or a plan being removed.
## IF We Implement the AI dashboard, The system also answers natural language questions like "How does WorldLink 300 Mbps compare to DishHome at the same speed?" using AI.

Live Features
•	Scrapes 4 ISPs automatically every 6 hours (WorldLink, Vianet, DishHome, CGNet)
•	Detects price changes, speed changes, bundle changes, and new or removed plans
•	Sends Slack and email alerts when competitors make significant moves
•	Stores 61+ live plans in a database with full history
•	Dashboard showing price comparison charts, market positioning, and a live change feed
•	AI-powered semantic search — ask questions in plain English and get answers
•	Weekly competitive intelligence report generated every Monday morning



Tech Stack
Layer	Technology
Backend API	FastAPI (Python)
Database	PostgreSQL
Task queue	Celery + Redis
Vector search	Qdrant
AI / LLM	Groq (llama-3.1-8b-instant)
Embeddings	Sentence Transformers (all-MiniLM-L6-v2)
Scrapers	httpx + BeautifulSoup, Playwright
Frontend	React + Vite + Tailwind CSS + Recharts
Containers	Docker + Docker Compose


Project Structure
worldlink-cip/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── plans.py        # Plan listing, comparison, history endpoints
│   │       ├── changes.py      # Change log endpoints
│   │       ├── rag.py          # AI semantic search endpoints
│   │       ├── reports.py      # Weekly reports and positioning endpoints
│   │       ├── scrape.py       # Manual scrape trigger endpoint
│   │       └── isps.py         # ISP listing endpoint
│   ├── ingestion/
│   │   ├── scrapers/
│   │   │   ├── worldlink_scraper.py
│   │   │   ├── vianet_scraper.py
│   │   │   ├── dishhome_scraper.py
│   │   │   └── cgnet_scraper.py
│   │   └── tasks/
│   │       ├── celery_app.py   # Celery config and Beat schedule
│   │       └── scrape_tasks.py # Celery tasks for each ISP
│   ├── detection/
│   │   └── change_detector.py # Compares new scraped data vs database
│   ├── normalization/
│   │   └── normalizer.py       # Converts raw scraped data to structured format
│   ├── intelligence/
│   │   └── rules_engine.py     # Rules for deciding alert severity
│   ├── alerts/
│   │   └── alert_dispatcher.py # Sends Slack and email alerts
│   ├── rag/
│   │   └── rag_service.py      # Qdrant vector search + Groq LLM
│   ├── reports/
│   │   └── report_generator.py # Weekly report generation
│   └── models/          

       # SQLAlchemy database models
├── frontend/
│   └── src/
│       ├── App.jsx             # Main dashboard
│       └── api.js              # API calls to FastAPI backend
├── alembic/                    # Database migrations
├── tests/                      # Unit tests
├── docker-compose.yml
├── Dockerfile
└── requirements.txt



Getting Started
Requirements
•	Docker Desktop installed and running
•	Node.js 20+ (for the frontend)
•	Git
1. Clone the repository
git clone https://github.com/your-username/worldlink-cip.git
cd worldlink-cip
2. Set up environment variables
Create a .env file in the project root:
# Database
DATABASE_URL=postgresql+asyncpg://cip_user:cip_password@postgres:5432/worldlink_cip
DATABASE_URL_SYNC=postgresql://cip_user:cip_password@postgres:5432/worldlink_cip

# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant (vector database)
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=cip_plans

# AI
GROQ_API_KEY=your_groq_api_key_here
GROQ_LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Alerts
SLACK_WEBHOOK_URL=your_slack_webhook_url
ALERT_EMAIL=intel@worldlink.com.np

# App
APP_ENV=development
APP_PORT=8000
Get a free Groq API key at console.groq.com.
3. Start the backend
docker compose up -d
This starts PostgreSQL, Redis, Qdrant, the FastAPI app, Celery worker, Celery Beat scheduler, and Flower (task monitor).
4. Run database migrations
docker compose exec app bash -c "cd /app && PYTHONPATH=/app alembic upgrade head"
5. Start the frontend
cd frontend
npm install
npm run dev
Open http://localhost:5173 in your browser.
________________________________________
API Endpoints
All endpoints are available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.
Plans
Method	Endpoint	Description
GET	/api/plans	List all active plans with filters
GET	/api/plans/compare	WorldLink vs competitor prices at each speed tier
GET	/api/plans/{id}	Single plan detail
GET	/api/plans/{id}/history	Price history for a plan

Filter options for /api/plans:
•	isp — filter by ISP slug (worldlink, vianet, dishhome, cgnet)
•	min_speed / max_speed — speed range in Mbps
•	max_price — maximum monthly price in NPR
•	bundle — filter by bundle type (iptv, router, ott)
Changes
Method	Endpoint	Description
GET	/api/changes	Recent change log with filters
GET	/api/changes/summary	Count of changes by type this week

AI Search
Method	Endpoint	Description
POST	/api/rag/query	Semantic search — find plans matching a description
POST	/api/rag/ask	Ask a question in plain English, get an AI answer
POST	/api/rag/reindex	Rebuild the Qdrant search index
Example — semantic search:
POST /api/rag/query
{ "q": "cheapest unlimited 300 Mbps plan", "limit": 5 }
Example — AI question:
POST /api/rag/ask
{ "question": "How does WorldLink compare to DishHome at 300 Mbps?" }

Reports
Method	Endpoint	Description
GET	/api/reports	List all past weekly reports
GET	/api/reports/latest	Latest weekly report
GET	/api/reports/positioning	Current WorldLink market position vs competitors
POST	/api/reports/generate	Generate a report on demand

How the Scraping Works
Each ISP has a dedicated scraper:
•	WorldLink — fetches worldlink.com.np homepage using httpx and parses plan cards with BeautifulSoup
•	Vianet — fetches vianet.com.np/vianetwifi6/ and parses the pricing tables (two rows of headers, data starts from row 2)
•	DishHome — uses Playwright to load the React SPA, intercepts the internal API call to dmnwebapi.dishhome.com.np/v1/internet/get-internet-packages, and parses the JSON response
•	CGNet — fetches cgnet.com.np/wifi-six using httpx and BeautifulSoup (note: CGNet may block requests from certain IP ranges)
After scraping, each plan goes through:
1.	Normalization — converts raw strings to typed data (speed to Mbps int, price to NPR float, bundle detection)
2.	Diff — compares against existing database records
3.	Change detection — any difference creates a change_log entry with severity rating
4.	Alerting — high/critical changes trigger Slack and email alerts
5.	Qdrant indexing — plans are embedded and stored for semantic search

Scrape Schedule
Celery Beat runs scrapers automatically:
Task	Schedule
All ISPs (full sweep)	Every 6 hours
WorldLink	Every 12 hours at :00
Vianet	Every 12 hours at :05
CGNet	Every 12 hours at :10
DishHome	Every 12 hours at :15
Weekly report	Every Monday at 8am NPT


Change Detection
The system compares these fields on every scrape:
•	price_monthly — triggers price_decrease or price_increase
•	download_mbps — triggers speed_change
•	bundle_flags — triggers bundle_added or bundle_removed
•	Plan appearing for first time — triggers plan_added
•	Plan disappearing from the site — triggers plan_removed
Severity levels:
Severity	Condition
Critical	Price change > 10%, or plan removed
High	New plan, bundle change, speed change
Medium	Price change 3–10%
Low	Price change < 3%


Dashboard
The frontend dashboard at http://localhost:5173 shows:
•	Stat cards — speed tiers tracked, WorldLink wins, coverage gaps, recent changes
•	Price comparison chart — bar chart comparing WorldLink vs competitor prices at each speed tier (green = WL cheaper, red = competitor cheaper, grey = no WL plan)
•	Market positioning table — detailed breakdown with diff percentages
•	Recent changes feed — severity-tagged list of recent plan changes
•	WorldLink vs Competitors table — filterable by speed tier

Monitoring
Flower (Celery task monitor) is available at http://localhost:5555. It shows:
•	Which tasks are running or queued
•	Task success/failure history
•	Worker status
Scrape run history is stored in the scrape_runs table:
SELECT isp_slug, status, plans_found, changes_detected, duration_ms, started_at
FROM scrape_runs
ORDER BY started_at DESC
LIMIT 20;

Running Tests
docker compose exec app bash -c "cd /app && PYTHONPATH=/app pytest tests/test_change_detector.py -v"

Known Limitations
•	C
•	
•	
•	GNet blocks scraper requests from some IP ranges (TLS-level rejection). Plans are seeded manually from the live site data.
•	DishHome requires Playwright (headless Chromium) because their site is a React SPA. This makes the DishHome scraper slower (~15 seconds) than the others (~2 seconds).
•	The RAG semantic search uses all-MiniLM-L6-v2, a general-purpose model. It works well for price/speed queries but may miss nuanced bundle comparisons.
•	Price history charts require at least 2 scrape cycles with a real price change to show a trend line.

Environment Services
Service	URL	Purpose
FastAPI	http://localhost:8000	Backend API
API Docs	http://localhost:8000/docs	Swagger UI
Dashboard	http://localhost:5173	Frontend
Flower	http://localhost:5555	Celery task monitor
PostgreSQL	localhost:5435	Database
Qdrant	http://localhost:6333	Vector search
Redis	localhost:6379	Task broker

Contributing
1.	Create a feature branch: git checkout -b feature/your-feature
2.	Make your changes
3.	Run tests: pytest tests/ -v
4.	Commit: git commit -m "add: your feature description"
5.	Push and open a pull request



