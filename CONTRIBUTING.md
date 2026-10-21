# Working together on this repository

`main` holds only reviewed work. Nobody commits or pushes to `main` directly; everything arrives through a pull
request.

## Branches

| Branch | Who | What |
|---|---|---|
| `main` | both, via pull request only | reviewed, working state; the pipeline and the tests pass |
| `<name>/<topic>` | one person | one piece of work, e.g. `soma/rescope`, `alex/slides` |

Use one branch per topic, not one per person forever. Short branches are easier to review and merge.

## Daily workflow

```bash
git switch main
git pull
git switch -c <name>/<topic>        # new work; or: git switch <name>/<topic> to continue
# ... edit, run the pipeline / tests ...
git add <files>
git commit -m "What changed and why"
git push -u origin <name>/<topic>
```

To get the latest `main` into your branch (do this before opening a pull request):

```bash
git switch main
git pull
git switch <name>/<topic>
git merge main                      # resolve conflicts, run the tests, commit
git push
```

## Pull requests

1. Open a pull request from your branch into `main` on GitHub.
2. The other person reviews it: is every number from `reports/key_numbers.yaml`, does `python -m pytest` pass, is every
   method decision logged in `docs/decision_log.md`?
3. Merge with "Create a merge commit" (keeps the history readable), then delete the branch.

## Rules

- Never force-push `main`, and never rewrite history that someone else may have pulled.
- `data/` and `reports/` are not committed (only `reports/final/project_summary.pdf`); rebuild them with
  `python -m study_program_intelligence.pipeline`.
- Never commit secrets: `.env` stays local.

## GitHub settings (owner, once)

Settings -> Branches -> Add branch protection rule for `main`:

- Require a pull request before merging, with 1 approval.
- Do not allow bypassing the above settings.
- Block force pushes and deletions.

Add the collaborator under Settings -> Collaborators.
