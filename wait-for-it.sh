
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 host[:port]"
  exit 1
fi

hostport="$1"
shift

case "$hostport" in
  *:*)
    HOST="${hostport%%:*}"
    PORT="${hostport##*:}"
    ;;
  *)
    HOST="$hostport"
    PORT="5432"
    ;;
esac

: "${POSTGRES_USER:?need POSTGRES_USER env var}"
: "${POSTGRES_PASSWORD:?need POSTGRES_PASSWORD env var}"
: "${POSTGRES_DB:?need POSTGRES_DB env var}"

echo "Waiting for Postgres at $HOST:$PORT ..."

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$HOST" -p "$PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' >/dev/null 2>&1; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - executing command"
exec "$@"
