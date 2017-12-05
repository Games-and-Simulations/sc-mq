#!/bin/bash
set -eux
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROJECT_PATH=$(dirname "${SCRIPT_PATH}")
source ${PROJECT_PATH}/docker/docker_config.sh
############################################################

# List of images to run by default
declare -a DOCKER_RUNS=(${DOCKER_TAG_RABBITMQ_BROKER} \
                        ${DOCKER_TAG_REPLAY_PARSER} \
                        )

# You can specify your own list
if [[ $# -gt 0 ]] ; then
    declare -a DOCKER_RUNS=("$@")
fi

[ -z "${DETACHED+x}" ] && DETACHED="-d"
[ -z "${ARGS+x}" ] && ARGS=""

function DOCKER_RUN() {
  RUN_IMAGE="$1"
  sudo -E docker run \
      --rm -it \
      ${DETACHED} \
      ${ARGS} \
      --env-file ${PROJECT_PATH}/config.env \
      --net host \
      --name ${RUN_IMAGE} \
      "${DOCKER_REPOSITORY}:${RUN_IMAGE}"
}

for DOCKER_RUN in "${DOCKER_RUNS[@]}"; do
  DOCKER_RUN ${DOCKER_RUN}
done
