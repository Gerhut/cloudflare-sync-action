FROM python

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off PIP_DISABLE_PIP_VERSION_CHECK=on
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

RUN mkdir -p /usr/local/app
WORKDIR /usr/local/app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

COPY . .
CMD ["python", "/usr/local/app"]
