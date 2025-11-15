FROM mcr.microsoft.com/playwright/python:v1.41.2-jammy

# Install required system dependencies (Playwright base image already includes Chromium)
# This image already runs Python 3.11 + Playwright dependencies + browsers.

WORKDIR /app

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install Python deps
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy app
COPY . /app

# Expose port (Railway uses $PORT)
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

