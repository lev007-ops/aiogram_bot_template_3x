FROM python:3.9
ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
