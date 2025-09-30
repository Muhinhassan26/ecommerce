# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally (goes to /root/.local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency definitions first (for better build caching)
COPY pyproject.toml uv.lock ./

# Install dependencies globally into the container environment
RUN uv sync --frozen --no-cache

# Copy the rest of the source code
COPY . .

# Create unprivileged user and switch to it
RUN addgroup --system fastapi && adduser --system --ingroup fastapi fastapi
USER fastapi

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
