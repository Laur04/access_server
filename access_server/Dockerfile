FROM python:3.8.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /home/access_server_user

RUN addgroup -S access_server_user && adduser -S access_server_user -G access_server_user

ENV HOME = /home/access_server_user
ENV APP_HOME=/home/access_server_user/access_server
ENV ANSIBLE_HOST_KEY_CHECKING=False
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/serve
RUN mkdir $APP_HOME/media
COPY . $APP_HOME

RUN chown -R access_server_user:access_server_user $APP_HOME

RUN apk update && apk add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev postgresql-dev python3-dev libpq openssl-dev cargo sshpass bash openssh openrc
RUN pip install --upgrade pip
RUN pip install -r $APP_HOME/requirements.txt

RUN chmod +x $APP_HOME/entrypoint.sh

WORKDIR $APP_HOME

ENTRYPOINT ["/home/access_server_user/access_server/entrypoint.sh"]