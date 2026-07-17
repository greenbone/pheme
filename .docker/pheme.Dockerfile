
FROM debian:stable-slim AS builder

ENV PATH="/root/.local/bin:${PATH}"

COPY . /source

WORKDIR /source

RUN apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
    python3 \
    python-is-python3 \
    pipx && \
    apt-get remove --purge --auto-remove -y && \
    rm -rf /var/lib/apt/lists/*

RUN pipx install poetry

RUN rm -rf dist && poetry build -f wheel

FROM debian:stable-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /pheme

RUN apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
    adduser \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    python3 \
    python3-pip && \
    apt-get remove --purge --auto-remove -y

RUN addgroup --gid 1001 --system pheme && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group pheme

COPY --from=builder /source/dist/* /pheme/

RUN python3 -m pip install --break-system-packages /pheme/*

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        uwsgi \
        uwsgi-plugin-python3 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
USER 1001:1001
CMD ["uwsgi", "--http-socket", ":8080", "--need-plugin", "python3", "--module", "pheme.wsgi:application", "--env", "DJANGO_SETTINGS_MODULE=pheme.settings", "--master", "--processes", "3", "--max-requests", "100", "--enable-threads", "--vacuum"]
