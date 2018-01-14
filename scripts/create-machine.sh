#!/usr/bin/env bash

if [[ ! -f "./env.config" ]]; then
    echo "Config file not found. Run this script from project root folder"
    exit
fi

source ./env.config

IS_RUN=$(docker-machine ls --filter "name=${ENV_NAME}" --filter "state=Running" -q)
if [[ -n "${IS_RUN}" ]]; then
  echo "- Machine already exists $?"
  exit
fi

docker-machine create -d "virtualbox" "${ENV_NAME}"
docker-machine ip "${ENV_NAME}"