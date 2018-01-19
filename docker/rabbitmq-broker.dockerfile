FROM rabbitmq:3.7.2-management

RUN rabbitmq-plugins enable --offline rabbitmq_management \
    && rabbitmq-plugins enable --offline rabbitmq_mqtt \
    && rabbitmq-plugins enable --offline rabbitmq_shovel \
    && rabbitmq-plugins enable --offline rabbitmq_shovel_management


ADD rabbitmq.config /etc/rabbitmq/
ADD definitions.json /etc/rabbitmq/

