#!/bin/sh
docker buildx build --cache-from=$REPO_USER/$REPO_NAME:cache --cache-to=$REPO_USER/$REPO_NAME:cache --platform linux/amd64,linux/arm/v7 --push -t $REPO_USER/$REPO_NAME:$COMMIT .