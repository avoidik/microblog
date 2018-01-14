#!/usr/bin/env bash

if [[ ! -f "./env.config" ]]; then
    echo "Config file not found. Run this script from project root folder"
    exit
fi

source ./env.config

IS_RUN=$(docker-machine ls --filter "name=${ENV_NAME}" --filter "state=Running" -q)
if [[ -z "${IS_RUN}" ]]; then
  echo "- Machine does not exists $?"
  exit
fi

eval "$(docker-machine env "${ENV_NAME}")"

echo -n "- Harmful operation. Continue with deletion? (y/n): "
read -r CONFIRMATION
if [[ "${CONFIRMATION}" != "y" ]] && [[ "${CONFIRMATION}" != "Y" ]]; then
    echo "- Aborted"
    exit
fi

docker network prune -f
docker system prune -f -a