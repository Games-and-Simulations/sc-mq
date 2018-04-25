#!/usr/bin/env bash

docker run \
      -d \
      --net host \
      --name rabbitmq-broker \
      --hostname $(hostname) \
      --restart=always \
      -v /data/rabbitmq:/var/lib/rabbitmq \
      "starcraft:rabbitmq-broker"


#docker stop $(docker ps -a -q) &
#docker update --restart=no $(docker ps -a -q) &
#systemctl restart docker
