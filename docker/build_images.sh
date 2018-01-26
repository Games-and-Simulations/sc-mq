#!/usr/bin/env bash
set -eux

docker build -f rabbitmq-broker.dockerfile  -t starcraft:rabbitmq-broker .
docker build -f replay-parser.dockerfile  -t starcraft:replay-parser .
