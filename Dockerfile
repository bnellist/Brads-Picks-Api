# Stage 1: Build dependencies
FROM python:3.11-slim-bullseye AS builder

WORKDIR /Brads-Picks-Api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Application
FROM python:3.11-slim-bullseye

WORKDIR /Brads-Picks-Api

COPY --from=builder /Brads-Picks-Api /Brads-Picks-Api
COPY . .

# Create a non-root user
RUN groupadd -r app && useradd -r -g app app

USER app
ENV PORT=8080
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "--user=app", "--group=app", "BradsPicks:app"]

