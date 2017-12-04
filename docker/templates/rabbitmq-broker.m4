FROM debian:jessie

include(`defaults.dockerfile')
include(`python.dockerfile')
include(`rabbitmq.dockerfile')

WORKDIR /app

COPY rabbitmq-broker/ /app

CMD ["/app/docker-entrypoint.sh"]
