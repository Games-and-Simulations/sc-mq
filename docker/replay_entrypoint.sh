#!/usr/bin/env bash
set -x

REPLAY_FILE=$1
PARSER_TIMEOUT=$2
LOG_FILE="${LOG_DIR}/replay_${REPLAY_FILE}.log"

. ./play_common.sh

function RUN_PARSER() {
    win_java32 \
        -jar \
        -Xmx1g \
        -Djava.net.preferIPv4Stack=true \
        bin/parser-jar-with-dependencies.jar \
            --file "${REPLAY_FILE}" \
    >>${LOG_FILE} 2>&1
}


start_gui
sleep 2
run_with_timeout ${PARSER_TIMEOUT} RUN_PARSER

IS_TIMED_OUT=$?
if [ ${IS_TIMED_OUT} -eq 143 ]; then
    LOG "Parsing timed out!" >> "$LOG_FILE"

    # Log ps aux for more info
    LOG "Running processes:" >> "$LOG_FILE"
    ps aux >> "$LOG_FILE"

    exit 1
else
    LOG "Parsing finished within timeout limit." >> "$LOG_FILE"
    LOG "Exit code: $IS_TIMED_OUT" >> "$LOG_FILE"
    exit $IS_TIMED_OUT
fi
