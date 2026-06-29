FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl wget gnupg libpq-dev gcc \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libgbm1 libasound2 libxshmfence1 libxrandr2 \
    libcups2 libxcomposite1 libxdamage1 libxfixes3 \
    libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium
RUN playwright install chromium 

# Pre-download embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

RUN mkdir -p logs

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
