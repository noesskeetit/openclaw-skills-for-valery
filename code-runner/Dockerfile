FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /skill
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN npm install -g typescript react react-dom

COPY scripts/ scripts/
COPY SKILL.md .

ENV WORKSPACE=/workspace
RUN mkdir -p /workspace

ENTRYPOINT ["python3"]
