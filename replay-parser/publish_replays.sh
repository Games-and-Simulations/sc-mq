#!/usr/bin/env bash
set -eu
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROJECT_PATH=$(dirname "${SCRIPT_PATH}")
####################################################

# Where to look for replays
[ -z "${REPLAY_BASE_PATH+x}" ] && REPLAY_BASE_PATH=/data/sscait_bot_replays

# any kind of combination
REPLAY_COMBINATION=""

# everything against protoss
#REPLAY_COMBINATION="(PvT|TvP|PvZ|ZvP|PvP|RvP|PvR)"
# everything against terran
#REPLAY_COMBINATION="(ZvT|TvZ|TvP|PvT|TvT|RvT|TvR)"
# everything against zerg
#REPLAY_COMBINATION="(ZvT|TvZ|ZvP|PvZ|ZvZ|RvZ|ZvR)"

find ${REPLAY_BASE_PATH} \
     -regextype posix-egrep \
     -iregex ".*$REPLAY_COMBINATION\.rep" \
     -print \
     -exec ${PROJECT_PATH}/replay-parser/publish_replay.sh {} \;
