FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig*.json vite.config.ts ./
COPY src ./src
RUN npm run build

FROM python:3.13-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/backend \
    FLARE_DATABASE_PATH=/state/flare_ai.sqlite3 \
    FLARE_SEED_ON_START=true FLARE_SERVE_FRONTEND=true PORT=8000
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --create-home flare \
    && mkdir /state && chown flare:flare /state
COPY backend/app ./backend/app
COPY data/psi_starter.json ./data/psi_starter.json
COPY data/raw/nasa ./data/raw/nasa
COPY --from=frontend /build/dist ./dist
USER flare
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/api/ready', timeout=3).close()"
CMD ["python", "-m", "app.run", "--host", "0.0.0.0"]
