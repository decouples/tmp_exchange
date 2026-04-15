ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential curl libglib2.0-0 libsm6 libxext6 libxrender1 \
      libgl1 poppler-utils \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r <(uv pip compile pyproject.toml --quiet) || \
    uv pip install --system --no-cache \
      "fastapi>=0.115" "uvicorn[standard]>=0.32" "pydantic>=2.9" "pydantic-settings>=2.6" \
      "sqlalchemy[asyncio]>=2.0" "asyncpg>=0.30" "aiosqlite>=0.20" "alembic>=1.14" \
      "arq>=0.26" "redis>=5.2" "minio>=7.2" "python-multipart>=0.0.12" \
      "python-jose[cryptography]>=3.3" "passlib[bcrypt]>=1.7" "httpx>=0.28" \
      "pillow>=11.0" "pymupdf>=1.25" "numpy>=2.1" "slowapi>=0.1.9" "websockets>=13.1" \
      "email-validator>=2.2"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
