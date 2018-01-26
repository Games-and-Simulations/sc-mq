FROM starcraft:game

USER starcraft
COPY --chown=starcraft:users replay_entrypoint.sh $APP_DIR/replay_entrypoint.sh
COPY --chown=starcraft:users replay_bwapi.ini "$BWAPI_DATA_DIR/bwapi.ini"
RUN cp /app/bwapi/human/BWAPI.dll /app/sc/bwapi-data/

RUN mkdir $APP_DIR/bin
RUN mkdir $APP_DIR/storage
VOLUME $APP_DIR/bin
VOLUME $APP_DIR/storage

WORKDIR $APP_DIR
