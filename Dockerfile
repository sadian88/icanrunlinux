FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY prisma/ prisma/
COPY scripts/ scripts/
COPY pyproject.toml .

RUN mkdir -p data && chmod +x scripts/entrypoint.sh

RUN prisma generate

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]
