FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG APP_UID=1000
ARG APP_GID=1000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY alembic ./alembic
COPY alembic.ini .

RUN groupadd --gid ${APP_GID} appuser \
    && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/data /app/uploads \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
