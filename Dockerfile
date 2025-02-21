# Use an official Python runtime as base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /Brads-Picks-Api

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# copy the rest of the application
COPY . .

# Set environmnet varibale for Flask
ENV FLASK_APP=BradsPicks.py
ENV FLASK_ENV=production

# Set environment variables
ENV PORT=8080

# Expose port 9090 for Cloud Run
EXPOSE 8080

# Command to run the app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080","BradsPicks:app"]
