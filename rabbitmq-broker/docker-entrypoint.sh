#!/usr/bin/env bash
set -euxm

# This entrypoint will setup multiple exchanges with their queues and dead letter queues.
# It's quite simplistic setup.

RABBITMQ_CALL() {
    ./rabbitmqadmin \
        -H ${RABBITMQ_BROKER_HOST} \
        -u ${RABBITMQ_DEFAULT_USER} \
        -p ${RABBITMQ_DEFAULT_PASS} \
        "$@"
}

DECLARE_QUEUE() {
  QUEUE=$1
  RABBITMQ_CALL declare exchange name=${QUEUE}         auto_delete=false durable=true type=direct internal=false
  RABBITMQ_CALL declare exchange name=${QUEUE}.dead    auto_delete=false durable=true type=direct internal=false

  RABBITMQ_CALL declare queue name=${QUEUE}.dead       auto_delete=false durable=true 'arguments={"exclusive":false}'
  RABBITMQ_CALL declare queue name=${QUEUE}            auto_delete=false durable=true "arguments={\"exclusive\":false, \"x-dead-letter-exchange\":\"${QUEUE}.dead\",\"x-dead-letter-routing-key\":\"${QUEUE}\"}"

  RABBITMQ_CALL declare binding source="${QUEUE}.dead" destination_type="queue" destination="${QUEUE}.dead" routing_key="${QUEUE}"
  RABBITMQ_CALL declare binding source="${QUEUE}"      destination_type="queue" destination="${QUEUE}"      routing_key="${QUEUE}.${QUEUE}"
}


export RABBITMQ_PID_FILE=/var/lib/rabbitmq/pid
./docker-rabbit.sh rabbitmq-server &
sleep 2
rabbitmqctl wait "${RABBITMQ_PID_FILE}"

DECLARE_QUEUE play
DECLARE_QUEUE play_results
DECLARE_QUEUE parse
DECLARE_QUEUE cluster_states
DECLARE_QUEUE learn_policy

# resume server
fg %1

