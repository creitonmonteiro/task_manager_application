FROM python:3.14-slim
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PIP_DEFAULT_TIMEOUT=120
ENV POETRY_REQUESTS_TIMEOUT=120

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock README.md alembic.ini ./
COPY migrations ./migrations
COPY task_manager ./task_manager
COPY entrypoint.sh ./entrypoint.sh

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --without dev
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]