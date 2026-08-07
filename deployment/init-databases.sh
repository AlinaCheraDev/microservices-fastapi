#!/bin/bash
set -e

create_user_and_database() {
	local database=$1
	local user=$2
	local password=$3
	echo "Creating database '$database' with user '$user'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $user WITH PASSWORD '$password';
	    CREATE DATABASE $database OWNER $user;
	    REVOKE CONNECT ON DATABASE $database FROM PUBLIC;
EOSQL
}

create_user_and_database "$ACCOUNTS_POSTGRES_DB" "$ACCOUNTS_POSTGRES_USER" "$ACCOUNTS_POSTGRES_PASSWORD"
create_user_and_database "$AUTH_POSTGRES_DB" "$AUTH_POSTGRES_USER" "$AUTH_POSTGRES_PASSWORD"
create_user_and_database "$PETS_POSTGRES_DB" "$PETS_POSTGRES_USER" "$PETS_POSTGRES_PASSWORD"