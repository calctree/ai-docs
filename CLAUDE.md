@AGENTS.md

## Working in this repo

`skills/calctree/` **is** the published skill. A push to `main` that touches it rebuilds and
republishes `calctree.zip` via `.github/workflows/release-skill.yml`, so a change here reaches
users without a further release step. Run the release testing in
[CONTRIBUTING.md](CONTRIBUTING.md) before pushing.

`context7.json` is the Context7 index config, not documentation — its `rules` are what an AI
sees when it looks CalcTree up. Keep them in step with `SKILL.md`.
