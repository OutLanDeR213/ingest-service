#!/bin/sh
set -e

# Импорт только если базы нет
if [ "$IMPORT_ON_START" = "true" ] && [ ! -f "/app/event_db_data/event_db.sqlite3" ]; then
    if [ -f "/app/data/events_sample.csv" ]; then
        python -m event_service.import_events /app/data/events_sample.csv
    fi
fi

exec "$@"
