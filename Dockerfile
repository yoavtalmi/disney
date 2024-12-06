# Use an official lightweight Python image
FROM python:3.10-slim

# Set environment variables to prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY data/ /app/data/
COPY .env /app/.env

COPY server.py /app/

EXPOSE 8000


ENV RUN_SETUP="false"

# Default entrypoint to check RUN_SETUP and prepare data if needed
CMD bash -c "\
    if [ \"$RUN_SETUP\" = \"true\" ]; then \
        python src/scrape_faq.py && python src/vectorizing.py; \
    fi; \
    python server.py"
