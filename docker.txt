# Use an official Python runtime as base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements fil
COPY requiremnets.txt .

# Install dependencies
RUN pip install --upgrade pip setuptools && pip install --no-cache-dir -r /app/requirements.txt

# copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080

# Expose port 9090 for Cloud Run
EXPOSE 8080

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "bradspicks:app"]
