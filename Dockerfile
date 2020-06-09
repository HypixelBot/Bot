FROM python:3.8
COPY ./ /srv/bot/
WORKDIR /srv/bot/
RUN pip install -r requirements.txt
CMD python ./bot.py