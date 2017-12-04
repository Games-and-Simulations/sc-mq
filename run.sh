#!/bin/bash
set -eux
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROJECT_PATH="${SCRIPT_PATH}"
source ${PROJECT_PATH}/docker/docker_config.sh
############################################################

sudo -E docker run \
    --rm -it -d \
    --env-file ${PROJECT_PATH}/rabbitmq-config.env \
    --net host \
    --name ${DOCKER_TAG_RABBITMQ_BROKER} \
    "${DOCKER_REPOSITORY}:${DOCKER_TAG_RABBITMQ_BROKER}"

