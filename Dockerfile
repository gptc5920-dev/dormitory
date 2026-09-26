FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    YOLO_CONFIG_DIR=/tmp/ultralytics

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config default-libmysqlclient-dev libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
# CPU wheels avoid bundling unused CUDA libraries on ordinary Coolify servers.
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision \
    && pip install -r requirements.txt

COPY . ./
RUN useradd --uid 10001 --create-home app \
    && mkdir -p /app/media /app/staticfiles /app/models \
    && chown -R app:app /app \
    && sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

USER app
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["serve"]
