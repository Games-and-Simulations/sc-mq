#!/bin/bash
set -eux
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROJECT_PATH=$(dirname "${SCRIPT_PATH}")
source ${PROJECT_PATH}/docker/docker_config.sh
############################################################

# List of images to build by default
declare -a DOCKER_BUILDS=(${DOCKER_TAG_RABBITMQ_BROKER} \
                          ${DOCKER_TAG_REPLAY_PARSER} \
                          )

# You can specify your own list
if [[ $# -gt 0 ]] ; then
    declare -a DOCKER_BUILDS=("$@")
fi

mkdir -p ${PROJECT_PATH}/docker/_build

# Prepare dockerfiles from m4 templates
for f in ${PROJECT_PATH}/docker/templates/*.m4; do
    base=$(basename "$f")
    tag=${base%.*}
    m4 -I "${PROJECT_PATH}/docker/templates" "${f}" > "${PROJECT_PATH}/docker/_build/${tag}.dockerfile"
done

# Export current version into the builds
VERSION=$(git rev-parse HEAD)
for DOCKER_BUILD in "${DOCKER_BUILDS[@]}";
do
    docker build -f "${PROJECT_PATH}/docker/_build/${DOCKER_BUILD}.dockerfile" \
        -t "${DOCKER_REPOSITORY}:${DOCKER_BUILD}" \
        -t "${DOCKER_REPOSITORY}:${DOCKER_BUILD}-${VERSION}" ${PROJECT_PATH}
done
