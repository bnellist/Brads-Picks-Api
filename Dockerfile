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


USER app
ENV PORT=8080
CMD ["python", "BradsPicks.py"]

