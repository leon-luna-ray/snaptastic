ARG PYTHON_VERSION=3.10-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

RUN apt-get update && apt-get install -y \
    curl \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn

WORKDIR /code/frontend

COPY frontend/package.json frontend/yarn.lock ./
COPY frontend/index.html ./
COPY frontend/vite.config.js ./


RUN yarn
RUN yarn build

WORKDIR /code
RUN pip install poetry
COPY pyproject.toml poetry.lock /code/
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root --no-interaction
COPY . /code



RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "snaptastic.wsgi"]
