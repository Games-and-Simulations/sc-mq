#!/usr/bin/env bash
set -eu
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROJECT_PATH=$(dirname "${SCRIPT_PATH}")
####################################################

# Replay file to publish
REPLAY_FILE="$1"

RABBITMQ_CALL() {
    ${PROJECT_PATH}/replay-parser/rabbitmqadmin \
        -H ${RABBITMQ_BROKER_HOST} \
        -u ${RABBITMQ_DEFAULT_USER} \
        -p ${RABBITMQ_DEFAULT_PASS} \
        "$@" > /dev/null
}

RABBITMQ_CALL publish \
  exchange=parse \
  routing_key=parse.parse \
  payload="$REPLAY_FILE"
