FROM python:3.13-slim

WORKDIR /app

# Install deps before copying source so this layer is cached across code-only changes
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -e .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "ui.webchat:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
