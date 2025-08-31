set -e

PROJECT_DIR="/home/reiberry/event_manager"
BACKUP_DIR="/home/reiberry/backups"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
TIMESTAMP=$(date +"%F_%H%M")
mkdir -p "$BACKUP_DIR"

docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/event_manager_${TIMESTAMP}.sql"

gzip -f "$BACKUP_DIR/event_manager_${TIMESTAMP}.sql"

find "$BACKUP_DIR" -type f -name "event_manager_*.sql.gz" -mtime +30 -delete
