FROM python:3.12-slim

# Metadata
LABEL maintainer="Atul Kamble <atulkamble@github>"
LABEL description="Flask pipeline app served by Gunicorn"

# Security: run as non-root user
RUN groupadd --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Install dependencies first (layer cache optimisation)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py gunicorn.conf.py ./
COPY templates/ templates/
COPY static/    static/

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]

