FROM python:3.9.17-slim-bullseye

WORKDIR /cwb

# Install app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our app files
COPY stickers.json .
COPY app ./app

CMD [ "python", "-m", "app" ]
