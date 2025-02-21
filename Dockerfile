FROM python:3.11-slim-bullseye

WORKDIR /Brads-Picks-Api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "BradsPicks:app"]
