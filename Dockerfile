# Stage 1: Install dependencies
FROM python:3.11-slim-bullseye AS builder
WORKDIR /Brads-Picks-Api
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create final image
FROM python:3.11-slim-bullseye
WORKDIR /Brads-Picks-Api
COPY --from=builder /Brads-Picks-Api /Brads-Picks-Api
COPY . .

# Set the PORT environment variable (important for Cloud Run)
ENV PORT=8080

# Expose port 8080
EXPOSE 8080

# Run Flask app directly
CMD ["python", "BradsPicks.py"]

