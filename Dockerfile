# MUST use the Playwright runtime image
FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

# Make working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt /app/

# Install dependencies (Playwright browsers already included)
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . /app

# Expose port
EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

