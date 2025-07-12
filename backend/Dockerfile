FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools and compilers
    gcc \
    g++ \
    python3-dev \
    make \
    cmake \
    # OCR dependencies
    tesseract-ocr \
    tesseract-ocr-eng \
    # PDF processing dependencies
    poppler-utils \
    ghostscript \
    # Database dependencies
    libpq-dev \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    # FAISS dependencies
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for better Python and pip behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies in the correct order
RUN pip install --no-cache-dir --upgrade pip && \
    # Install numerical/scientific computing dependencies first
    pip install --no-cache-dir \
        numpy>=1.24.0 \
        scipy>=1.11.0 && \
    # Install FAISS for vector similarity search
    pip install --no-cache-dir faiss-cpu>=1.7.4 && \
    # Install PDF processing dependencies
    pip install --no-cache-dir \
        pdf2image>=1.16.3 \
        Pillow>=10.0.0 \
        pymupdf>=1.22.5 \
        pytesseract>=0.3.10 \
        weasyprint>=65.0 \
        python-docx>=1.0.0 && \
    # Install ML/NLP dependencies
    pip install --no-cache-dir \
        scikit-learn>=1.3.0 \
        spacy>=3.7.2 \
        yake>=0.4.8 \
        keybert>=0.7.0 \
        sentence-transformers>=2.2.2 && \
    # Download spaCy model
    python -m spacy download en_core_web_lg && \
    # Install remaining dependencies
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p \
    migrations/versions \
    storage/pdfs \
    storage/templates

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy application code
COPY . .
COPY migrations migrations/
COPY alembic.ini .

# Expose ports
EXPOSE 8000 5678

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["serve"]
