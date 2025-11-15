# Use Playwright 1.56 image (required for your installed version)
FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

# Copy requirements
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . /app

# Railway sets PORT; fallback to 8000
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


