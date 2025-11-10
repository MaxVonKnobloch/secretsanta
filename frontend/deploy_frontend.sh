#!/usr/bin/env bash

cd frontend
npm run build
rsync -av --delete build/ home-server:/var/www/secretsanta/
cd ..
rsync -av --delete static/users home-server:/var/www/secretsanta/static/users
rsync -av --delete static/previews home-server:/var/www/secretsanta/static/previews