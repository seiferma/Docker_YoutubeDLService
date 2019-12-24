FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    apk --no-cache add ffmpeg

COPY . .

EXPOSE 8080

CMD [ "python", "./main.py" ]
