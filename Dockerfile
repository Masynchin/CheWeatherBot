FROM python:3.9.17-slim-bullseye

WORKDIR /cwb

# Install app dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy our app files
COPY stickers.json .
COPY app ./app

ENTRYPOINT [ "python", "-m", "app" ]
