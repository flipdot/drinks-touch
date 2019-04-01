FROM python

RUN apt-get update && \
    apt-get install -y libsasl2-dev libldap2-dev locales && \
    rm -rf /var/lib/apt/lists/*
RUN localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
RUN mkdir /app

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./drinks_touch .

ENTRYPOINT ./game.py
