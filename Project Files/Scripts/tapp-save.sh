#!/usr/bin/env bash
#
# tapp-save.sh — commit and push the tracked TAPP record to GitHub.
#
#   tapp-save                     snapshot with an auto-generated message
#   tapp-save "Bump EPMA to v26"  snapshot with your own message
#   tapp-save -n                  preview only; changes nothing
#
# Only the paths allowlisted in .gitignore are touched. The per-technique
# paper folders are never staged.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"

if [ ! -d .git ]; then
    echo "error: $REPO is not a git repository" >&2
    exit 1
fi

DRY=0
if [ "${1:-}" = "-n" ] || [ "${1:-}" = "--dry-run" ]; then
    DRY=1
    shift
fi

# Unstage everything, working whether or not HEAD exists yet.
unstage() {
    if git rev-parse --verify -q HEAD >/dev/null; then
        git reset -q
    else
        git rm -rq --cached . >/dev/null 2>&1 || true
    fi
}

# --- what changed -----------------------------------------------------------
git add -A

if git diff --cached --quiet; then
    echo "Nothing to save — the record is already up to date."
    exit 0
fi

echo "Changes to be saved:"
echo
git diff --cached --stat | sed 's/^/  /'
echo

# --- refuse anything GitHub will reject -------------------------------------
BIG=$(git diff --cached --name-only -z | xargs -0 -I{} sh -c \
      'test -f "{}" && find "{}" -size +95M' 2>/dev/null || true)
if [ -n "$BIG" ]; then
    echo "error: these files exceed GitHub's 100 MB limit:" >&2
    echo "$BIG" | sed 's/^/  /' >&2
    echo "Add them to .gitignore or use Git LFS, then re-run." >&2
    unstage
    exit 1
fi

if [ "$DRY" -eq 1 ]; then
    echo "(dry run — nothing committed)"
    unstage
    exit 0
fi

# --- commit -----------------------------------------------------------------
if [ $# -gt 0 ]; then
    MSG="$*"
else
    N=$(git diff --cached --name-only | wc -l | tr -d ' ')
    MSG="TAPP snapshot $(date '+%Y-%m-%d %H:%M') — $N file(s) changed"
fi

git commit -q -m "$MSG"
echo "Committed: $MSG"

# --- push -------------------------------------------------------------------
if ! git remote get-url origin >/dev/null 2>&1; then
    echo
    echo "No 'origin' remote is configured, so nothing was pushed."
    echo "Add one with:  git remote add origin <your-repo-url>"
    exit 0
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Pushing $BRANCH to origin..."
if git push -u origin "$BRANCH"; then
    echo "Pushed. GitHub is up to date."
else
    echo
    echo "Push failed. The commit is safe locally — fix the connection or"
    echo "authentication and run:  git push -u origin $BRANCH" >&2
    exit 1
fi
