FROM ghcr.io/astral-sh/uv:0.11.14 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /uvx /bin/
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
CMD ["uv", "run", "--frozen", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
