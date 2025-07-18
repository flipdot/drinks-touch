FROM node:22.17.1-alpine AS base-image

ENV CI=true

WORKDIR /srv/app/

RUN corepack enable


FROM base-image AS prepare

COPY ./pnpm-lock.yaml package.json ./

RUN pnpm fetch

COPY ./ ./

RUN pnpm install --offline


######################################################################
# Stage name "development" is required for development with dargstack.
FROM python:3.13.5-slim AS development

ENV PYTHONUNBUFFERED=1

WORKDIR /srv/app/

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
    apt-get install --no-install-recommends -y locales xinput \
    \
    libsdl1.2-dev libfreetype6-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libsdl-ttf2.0-dev libportmidi-dev build-essential && \
    \
    rm -rf /var/lib/apt/lists/* && \
    \
    localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8 && \
    \
    pip install poetry==1.8.2

COPY ./docker/asound.conf /etc/asound.conf
COPY ./docker/pip_extra-index-piwheels.conf /etc/pip.conf
COPY ./poetry.lock ./pyproject.toml ./
COPY --from=prepare /srv/app/package.json /dev/null

RUN --mount=type=cache,target=/root/.cache/pypoetry/cache \
    --mount=type=cache,target=/root/.cache/pypoetry/artifacts \
    poetry install

COPY ./drinks_touch/ ./drinks_touch/

ENV ENV=PI

ENTRYPOINT ["poetry", "run"]

#CMD ["python", "game.py"]
CMD ["python", "./drinks_touch/game.py"]
