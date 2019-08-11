FROM python

# old pygame dependency list
#
# git python3-dev python3-setuptools python3-numpy python3-opengl \
# libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
# libsdl1.2-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
# libtiff5-dev libx11-6 libx11-dev fluid-soundfont-gm timgm6mb-soundfont \
# xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic fontconfig fonts-freefont-ttf libfreetype6-dev \

#libxml2-dev libxslt1-dev

# ignored pygame dependencies
#
# libjpeg-dev libpng-dev

# dependecies for this app, pygame, sqlalchemy.
RUN apt-get update && \
    apt-get install -y libldap2-dev libsasl2-dev locales \
    \
    python3-ldap python3-lxml python3-psycopg2 python3-pygame \
    \
    libsdl1.2-dev libfreetype6-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libsdl-ttf2.0-dev libportmidi-dev && \
    \
    rm -rf /var/lib/apt/lists/*
RUN localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
RUN mkdir /app/

WORKDIR /app/

COPY ./requirements-docker.txt ./
RUN pip install -r requirements-docker.txt

COPY ./drinks_touch/ ./

ENTRYPOINT ./game.py
