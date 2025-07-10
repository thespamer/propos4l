FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies including WeasyPrint requirements
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libpango1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi7 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt alembic psycopg2-binary weasyprint

# For development: install additional tools
RUN pip install --no-cache-dir debugpy pytest pytest-asyncio

# Create migrations directory
RUN mkdir -p migrations/versions

# Create storage directories
RUN mkdir -p storage/pdfs storage/templates

# Create entrypoint script with debug support
RUN echo '#!/bin/sh\n\
if [ "$1" = "migrate" ]; then\n\
    alembic upgrade head\n\
elif [ "$1" = "debug" ]; then\n\
    python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n\
else\n\
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n\
fi' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Copy application code
COPY . .

# Copy migration files
COPY migrations migrations/
COPY alembic.ini .

# Expose ports
EXPOSE 8000 5678

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["serve"]
