ARG HUB_U=amd64

FROM $HUB_U/python

ARG QEMUARCH=amd64

__MULTIARCH_COPY docker/build/qemu-${QEMUARCH}-static /usr/bin/
RUN apt-get update && \
    apt-get install -y libldap2-dev libsasl2-dev locales \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
    libsdl1.2-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    libtiff5-dev libx11-6 libx11-dev fluid-soundfont-gm timgm6mb-soundfont \
    xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic fontconfig fonts-freefont-ttf libfreetype6-dev && \
    rm -rf /var/lib/apt/lists/*
RUN localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
RUN mkdir /app/

WORKDIR /app/

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
__MULTIARCH_RUN rm /usr/bin/qemu-${QEMUARCH}-static

COPY ./drinks_touch/ ./

ENTRYPOINT ./game.py
