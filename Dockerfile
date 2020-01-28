FROM python:3.6

RUN apt-get update && apt-get -y install cron

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000 

RUN touch /var/log/cron.log

RUN crontab update_db.txt

CMD cron && sh start_server.sh
