FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    libreoffice-calc \
    libreoffice-writer \
    libreoffice-impress \
    poppler-utils \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /skill
COPY requirements.txt package.json ./
RUN pip install --no-cache-dir -r requirements.txt
RUN npm install --production
COPY scripts/ scripts/
COPY SKILL.md .

ENTRYPOINT ["python3"]
