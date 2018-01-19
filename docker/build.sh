#!/usr/bin/env bash
set -eux

docker build -f rabbitmq-broker.dockerfile  -t starcraft:rabbitmq-broker .
