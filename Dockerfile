# Use the Selenium Standalone Chrome image as the base
FROM selenium/standalone-chrome:latest

# Install Python and required dependencies
USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
WORKDIR /app
RUN python3 -m venv /app/venv

# Activate the virtual environment and install dependencies
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY src/ /app/src/
COPY data/ /app/data/
COPY .env /app/
COPY server.py /app/

# Set environment variables
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:$PATH"
ENV RUN_SETUP="false"

# Expose the Flask app port
EXPOSE 8000

# Default entrypoint to check RUN_SETUP and prepare data if needed
CMD bash -c "\
    if [ \"$RUN_SETUP\" = \"true\" ]; then \
        python src/scrape_faq.py && python src/vectorizing.py; \
    fi; \
    python server.py"
