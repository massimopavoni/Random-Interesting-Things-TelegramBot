FROM python:3.10.2-slim-buster

WORKDIR Random-Interesting-Things-TelegramBot

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY bot/ bot/

ARG TOKEN
ARG ADMIN
ARG CHANNEL
ARG LINKS_KEY
ENV TELEGRAM_BOT_TOKEN=$TOKEN
ENV TELEGRAM_ADMIN_USER_ID=$ADMIN
ENV TELEGRAM_CHANNEL_ID=$CHANNEL
ENV KUTT_API_KEY=$LINKS_KEY

CMD [ "python", "bot/main.py" ]