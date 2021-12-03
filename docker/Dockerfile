FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc make git libc-dev
RUN pip install "poetry>=1.0"

WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction

COPY src src
COPY docker/boot.sh .

ARG PORT=8000
ENV PORT=$PORT

ENTRYPOINT ["/app/boot.sh"]
CMD ["server"]
