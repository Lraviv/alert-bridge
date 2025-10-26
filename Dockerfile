FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create failed_alerts directory
RUN mkdir -p failed_alerts

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
