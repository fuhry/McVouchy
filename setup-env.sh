#!/bin/bash

set -eu
shopt -s nullglob

SCRIPT="$(readlink -f "$0")"
REPO_BASE="$(cd "$(dirname "$SCRIPT")"; pwd)"

HOOKS=($(cd "$REPO_BASE/git-hooks"; echo *.sh))
HOOKS=("${HOOKS[@]%.sh}")

if ! [[ -d "$REPO_BASE/.git/hooks" ]]; then
	echo "ERROR: $REPO_BASE is not a git repository." >&2
	exit 1
fi

for HOOK in "${HOOKS[@]}"; do
	test -h "$REPO_BASE/.git/hooks/$HOOK" && rm -f "$REPO_BASE/.git/hooks/$HOOK"
	if ! [[ -x "$REPO_BASE/git-hooks/$HOOK.sh" ]]; then
		echo "Skipping hook $HOOK: not marked as executable" >&2
		continue
	fi
	echo "Setting up git hook: .git/hooks/$HOOK -> git-hooks/$HOOK.sh"
	ln -sf "../../git-hooks/$HOOK.sh" "$REPO_BASE/.git/hooks/$HOOK"
done

