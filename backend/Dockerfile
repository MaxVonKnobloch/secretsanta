# Backend image for Secret Santa
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies needed for building wheels (e.g. pillow)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates build-essential libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only backend sources (put them under /app/backend so uv can run inside that folder)
COPY backend /app/backend

# Install Python tooling and dependencies into global Python environment
WORKDIR /app/backend
RUN pip install --upgrade pip setuptools wheel \
    && pip install uv \
    && uv pip install --system -r <(uv pip compile pyproject.toml)

# Initialize the database
WORKDIR /app
RUN python backend/init_db.py

EXPOSE 8000

# Run uvicorn directly (now available in global Python environment)
WORKDIR /app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
