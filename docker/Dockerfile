FROM python:alpine

WORKDIR /app

# Prepare shell entrypoint
COPY docker/entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Switch to a non-root user
RUN adduser -D -u 1000 user
RUN chown -R user:user /app
USER user

# Install dependencies
COPY docker/requirements.txt .
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt

# The application
COPY query_quickgo.py .

ENTRYPOINT ["/bin/sh", "./entrypoint.sh"]