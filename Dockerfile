# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (needed by psycopg2) and netcat for wait script
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev netcat \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"  
# uv installer adds to ~/.cargo/bin


# Copy dependency list first for caching
COPY pyproject.toml uv.lock ./ 
# If you use poetry/pdm adjust this step; for now we’ll use pip
# Make sure you generate a requirements.txt
RUN uv sync --frozen --no-cache


# Copy the rest of the source code
COPY . .

# Create unprivileged user
RUN addgroup --system fastapi && adduser --system --ingroup fastapi fastapi
USER fastapi

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
