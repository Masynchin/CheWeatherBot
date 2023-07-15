# Build
FROM python:3.9.17-slim-bullseye AS build

WORKDIR /source

## Install dependencies dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc-dev

## Install app dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /source/wheels -r requirements.txt

# Runtime
FROM python:3.9.17-slim-bullseye AS runtime

WORKDIR /cwb

## Build wheels
COPY --from=build /source/wheels /wheels
COPY --from=build /source/requirements.txt .
RUN pip install --no-cache /wheels/*

## Copy our app files
COPY stickers.json .
COPY app ./app

CMD [ "python", "-m", "app" ]
