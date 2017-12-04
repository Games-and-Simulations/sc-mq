# Default ENV settings

ENV GOSU_VERSION 1.10
ENV GOSU_GPG_KEY B42F6819007F00F88E364FD4036A9C25BF357DD4

ENV RABBITMQ_VERSION 3.6.12
ENV RABBITMQ_DEBIAN_VERSION 3.6.12-1
ENV RABBITMQ_GPG_KEY 0A9AF2115F4687BD29803A206B73A36E6026DFCA

# get logs to stdout
ENV RABBITMQ_LOGS=- RABBITMQ_SASL_LOGS=-

# /usr/sbin/rabbitmq-server has some irritating behavior, and only exists to "su - rabbitmq /usr/lib/rabbitmq/bin/rabbitmq-server ..."
ENV PATH /usr/lib/rabbitmq/bin:$PATH

# set home so that any `--user` knows where to put the erlang cookie
ENV HOME /var/lib/rabbitmq

ENV PYTHON_VERSION 3.6.1
ENV PYTHON_PIP_VERSION 9.0.1
ENV PYTHON_GPG_KEY 0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH
# solves http://bugs.python.org/issue19846
ENV LANG C.UTF-8


# Default tools we want in every image
RUN apt-get update && apt-get install -y --no-install-recommends \
        joe \
        wget \
        telnet; \
    rm -rf /var/lib/apt/lists/*
