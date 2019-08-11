FROM python

RUN apt-get update && \
    apt-get install -y libldap2-dev libsasl2-dev locales \
    \
    libsdl1.2-dev libfreetype6-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libsdl-ttf2.0-dev libportmidi-dev && \
    \
    rm -rf /var/lib/apt/lists/*
RUN localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
RUN mkdir /app/

WORKDIR /app/

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./drinks_touch/ ./

ENTRYPOINT ./game.py
