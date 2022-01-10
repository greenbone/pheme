FROM debian:stable-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /pheme

RUN apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    python3 \
    python3-pip && \
    apt-get remove --purge --auto-remove -y && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --gid 1001 --system pheme && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group pheme

COPY dist/* /pheme

RUN python3 -m pip install /pheme/*
