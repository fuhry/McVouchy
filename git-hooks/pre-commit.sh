#!/bin/bash

set -eu

SCRIPT="$(readlink -f "$0")"
REPO_BASE=$(cd $(dirname "$SCRIPT")/..; pwd)

for CMD in mypy black; do
	if ! which "$CMD" >/dev/null 2>&1; then
		echo "ERROR: $CMD is not installed. Please install it using your distribution's" >&2
		echo "ERROR: package manager prior to committing." >&2
		exit 1
	fi
done

echo "Running mypy..."
if ! mypy "$REPO_BASE"; then
	echo 'ERROR: mypy raised errors. Please correct them before committing.' >&2
	exit 1
fi

if ! black --check "$REPO_BASE"; then
	echo 'ERROR: Some files are not properly formatted.' >&2
	echo 'ERROR: Please run `black .` in '"$REPO_BASE"' prior to committing.' >&2
	exit 1
fi
