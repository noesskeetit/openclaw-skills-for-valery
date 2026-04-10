FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-rus \
    pandoc \
    libgl1 \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /skill
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts/ scripts/
COPY SKILL.md .

ENTRYPOINT ["python3"]
