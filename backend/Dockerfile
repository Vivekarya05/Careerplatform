FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    latexmk \
    lmodern \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-latex-extra \
  && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml ./
COPY backend/app ./app
COPY resume ./resume

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
