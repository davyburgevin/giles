#!/usr/bin/env bash
set -euo pipefail
# Always propose into Giles; never write NousResearch or merge automatically.
git remote remove upstream 2>/dev/null || true
git remote add upstream https://github.com/NousResearch/hermes-agent.git
git fetch upstream main --no-tags
if git merge-base --is-ancestor upstream/main HEAD; then
  echo 'Giles already contains upstream/main.'
  exit 0
fi
branch="giles/sync-$(git rev-parse --short=12 upstream/main)"
if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  echo "A synchronization branch already exists: $branch"
  exit 0
fi
git switch -c "$branch"
if git merge --no-edit upstream/main; then
  mkdir -p .github/upstream-workflows
  for file in .github/workflows/*; do
    case "$(basename "$file")" in giles-*) continue ;; esac
    git mv "$file" .github/upstream-workflows/
  done
  if ! git diff --cached --quiet; then
    git commit -m 'Keep upstream automation archived in Giles'
  fi
  draft=()
  note='Upstream was merged into this proposal. Review and pass Giles checks before merging.'
else
  # Preserve conflicts as a reviewable proposal; main and releases stay intact.
  conflicts=$(git diff --name-only --diff-filter=U)
  git merge --abort
  printf '%s\n' "$conflicts" > UPSTREAM_CONFLICTS.txt
  git add UPSTREAM_CONFLICTS.txt
  git commit -m 'Record upstream integration conflicts for manual resolution'
  draft=(--draft)
  note="Integration needs conflict resolution. Upstream commit: $(git rev-parse upstream/main). The PR records affected files; no engine update has been applied."
fi
git push origin "$branch"
printf '%s\n' "$note" > /tmp/giles-sync-pr.md
gh pr create --repo davyburgevin/giles --base main --head "$branch" "${draft[@]}" --title "Sync NousResearch $(git rev-parse --short=12 upstream/main)" --body-file /tmp/giles-sync-pr.md
