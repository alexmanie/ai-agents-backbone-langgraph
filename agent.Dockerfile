FROM python:3.11

ENV CONTAINER_HOME=/var/www

WORKDIR $CONTAINER_HOME
COPY ai-agent/requirements.txt .

RUN pip3 install -r requirements.txt

COPY ai-agent/. .

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]