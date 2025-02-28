FROM python:3.13-slim

# Install build dependencies for PDF packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    # WeasyPrint build dependencies
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Test WeasyPrint installation
RUN pip install --verbose WeasyPrint==60.2 && \
    pip install --verbose reportlab==4.1.0 && \
    echo "PDF dependencies installed successfully!" 