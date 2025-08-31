set -e
host="$1"
shift
until POSTGRES_PASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -c '\l' >/dev/null 2>&1; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done
>&2 echo "Postgres is up - executing command"
exec "$@"
