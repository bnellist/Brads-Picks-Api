# Use an official Python runtime as base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080

# Expose port 9090 for Cloud Run
EXPOSE 8080

# Command to run the app
CMD ["flask", "run", "--host", 0.0.0.0"]
