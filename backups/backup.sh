#!/bin/bash

ENV_FILE="/home/opc/homelab/second-brain/.env"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +
else
  echo "Error: .env file not found in $ENV_FILE."
  exit 1
fi

BACKUP_DIR="/home/opc/homelab/backups"
DATE=$(date +"%Y%m%d_%H%M")
FILE_NAME="nocodb_$DATE.sql.gz"
LOCAL_PATH="$BACKUP_DIR/$FILE_NAME"

REMOTE_NAME="gdrive"
REMOTE_DIR="$REMOTE_NAME:Rclone/SecondBrain"

mkdir -p "$BACKUP_DIR"

docker exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$LOCAL_PATH"

# Syncing with Google Drive
rclone copy "$LOCAL_PATH" "$REMOTE_DIR"

# Remote cleaning (keep only last 3 days backups)
rclone delete "$REMOTE_DIR" --min-age 3d

# Local cleaning
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +3 -exec rm {} \;

echo "Backup $FILE_NAME successful."