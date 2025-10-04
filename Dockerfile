# Dockerfile for CDR Generator
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the generator code
COPY . .

# Default command runs generator with config.yaml
CMD ["python", "cdr_generator.py", "--config", "config.yaml"]
