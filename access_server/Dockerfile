FROM python:3.8.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /home/access_server_user

RUN addgroup -S access_server_user && adduser -S access_server_user -G access_server_user

ENV HOME = /home/access_server_user
ENV APP_HOME=/home/access_server_user/access_server
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/serve
RUN mkdir $APP_HOME/media
WORKDIR $HOME
COPY . $APP_HOME
COPY manage.py $HOME/manage.py

RUN chown -R access_server_user:access_server_user $APP_HOME

RUN apk update && apk add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev postgresql-dev python3-dev libpq openssl-dev cargo
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x $APP_HOME/entrypoint.sh

USER access_server_user

ENTRYPOINT ["/home/access_server_user/access_server/entrypoint.sh"]