FROM python:3.12-slim-bullseye

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY ./manage.py ./manage.py
COPY ./snaptastic/ ./snaptastic/
COPY ./apps/ ./apps/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "snaptastic.wsgi"]
