# Image that runs the Python pipeline (the "pipeline" service in docker-compose).
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so this layer is cached unless requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project (see .dockerignore for what is excluded).
COPY . .

# Default command: run the full pipeline. Override with e.g.
#   docker compose run --rm pipeline python run.py --stage ingest
CMD ["python", "run.py"]
