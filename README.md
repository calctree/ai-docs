# calctree-skills

Turn engineering calculations into AI-callable tools with
[CalcTree](https://www.calctree.com). A CalcTree **page** is a calculation graph that
evaluates server-side with real units. This repo gives your AI the skill to discover pages
in a workspace, execute them with custom inputs, and build new ones.

## Layout

```
skills/building-calctree-calculations/
  SKILL.md                    the skill: read this first
  REFERENCE.md                every GraphQL document, for driving it without our code
  scripts/calctree_api.py     the primitives: stdlib only, importable and a CLI
  examples/smoke_two_page.py  end-to-end example
tools/package_skill.py        builds the distributable zip
.claude-plugin/               Claude Code plugin + marketplace manifests
AGENTS.md                     entry point for agent tools that look for it
evals/                        three evaluation scenarios
llms.txt                      machine-readable index
```


## Quick start: use a page as a tool

```bash
export CALCTREE_API_KEY=...
python3 skills/building-calctree-calculations/scripts/calctree_api.py pages <workspaceId>
python3 skills/building-calctree-calculations/scripts/calctree_api.py execute <workspaceId> <pageId> span="10 m"
```

No install: standard library only, no pip, no Node. To verify writes work too, run the
smoke test (creates two real pages, so point it at a workspace you do not mind writing to):

```bash
python3 skills/building-calctree-calculations/examples/smoke_two_page.py <workspaceId>
```

## Installing it

| Surface | How |
|---|---|
| Claude Code | `/plugin marketplace add calctree/calctree-skills` then `/plugin install calctree@calctree`, or copy the skill folder into `~/.claude/skills/` |
| claude.ai, desktop, Cowork | `python3 tools/package_skill.py`, then upload `dist/*.zip` under Settings > Features |
| Claude API | the same zip via `POST /v1/skills`. Note that surface has no network access, so only the guidance is usable there, not the write path |
| Cursor, Codex, other agent tools | point them at `AGENTS.md` |

Network access is required for everything except reading the guidance. On claude.ai, Free/Pro/Max
users toggle it in settings; Team and Enterprise admins allowlist `graph.calctree.com`.

Four things that catch everyone out, all covered in the skill:

1. **Dataset variables (VLOOKUP) are not in the `simpleCalculate` scope.** Pages that rely
   on VLOOKUP cannot be fully executed via the tool-use API path.
2. **A page must be registered in the page tree.** A page that exists but is not in the tree
   is orphaned and invisible.
3. **Evaluation is asynchronous.** Settle about two seconds after a write before reading, or
   you may read zero statements.
4. **An invalid API key does not say so.** It comes back as a GraphQL `"Unexpected error."`
   with no 401 and no mention of auth.

## Testing before this goes public

Four things have to hold: it installs, it runs on a clean machine, a model actually uses it
correctly, and nothing secret ships. Work top to bottom — each stage assumes the one above
passed.

### 1. Clean machine

The point of the Python rewrite is that this needs nothing but `python3`. Prove it somewhere
with no Node, no `pip install`, and no other CalcTree checkout.

```bash
export CALCTREE_API_KEY=...
python3 skills/building-calctree-calculations/examples/smoke_two_page.py <workspaceId>
```

Passes when: two page URLs print, `M_max = 360`, titles report `verified=True`, and page B
shows the reference snapshot of page A's values. Needs `python3` (3.9 is the oldest tested) and
network egress to `graph.calctree.com` and `api.calctree.com`.

Then the CLI path, which is how an agent with only a shell drives it:

```bash
python3 skills/building-calctree-calculations/scripts/calctree_api.py build <workspaceId> "Test" page.mdx
python3 skills/building-calctree-calculations/scripts/calctree_api.py context <workspaceId> <pageId>
```

### 2. Install, per surface

| Surface | How | Passes when |
|---|---|---|
| Claude Code, plugin | `/plugin marketplace add .` then `/plugin install calctree@calctree` | the skill triggers on a CalcTree request. **Untested — the `"source": "./"` layout has never been verified** |
| Claude Code, manual | copy the skill folder into `~/.claude/skills/` | same |
| claude.ai, desktop, Cowork | `python3 tools/package_skill.py`, upload `dist/*.zip` under Settings > Features | upload accepted (rejects files loose at the zip root), and a write succeeds — needs network access enabled for the sandbox |
| Claude API | the same zip via `POST /v1/skills` | guidance loads. Writes **cannot** work there: that sandbox has no network |
| Cursor, Codex, other agent tools | point them at `AGENTS.md` | they follow it to `SKILL.md` and drive the API |

### 3. Behaviour

Run the three scenarios in `evals/building-calctree-calculations.jsonl` and judge each against
its `expected_behavior`. Then check the specific traps that have actually caused bad pages:

- **Statement titles report `verified=True`.** The retry is load-bearing — roughly one run in
  three needs a second attempt, and the failure mode is a page that looks fine and is
  permanently untitled.
- **A bad key gives the translated error**, not a bare `"Unexpected error."`
- **The page is registered in the tree** — visible in the UI, not orphaned.
- **Reads settle** — no zero-statement reads straight after a write.
- **Units flow** — values carry their unit; no unit written into a column heading, no value
  stripped to a bare number.
- **A pass/fail check is a named boolean**, never a string ternary.
- **`<` and `>` are escaped** in prose as well as in formulas.
- **Variables do not collide with unit abbreviations** (`M_max`, not `M`).

### 4. Models

Test with Haiku, Sonnet and Opus. Only Opus has driven this so far. The authoring rules in
sections 5–8 of the skill are prose-heavy, so Haiku is where thin guidance will show first.

### 5. Secrets and hygiene

- No live credential anywhere in the tree or in history. A key was previously committed and has
  been rotated; check again before publishing.
- No `.env`, no `.claude/settings.local.json`, no `dist/`.
- `LICENSE` present, and `plugin.json` records it.

### 6. Clean up after yourself

Every test above writes real pages. Deleting one is a **soft** delete, so they keep coming back
from the `pages` query and accumulate:

```bash
python3 .../calctree_api.py audit <workspaceId> <pageId>...   # find untitled statements
python3 .../calctree_api.py delete <workspaceId> <pageId>     # soft delete
```

### Known gaps at time of writing

The plugin install path is unverified, only Opus has been tested, and
`skills/connection-node-testing/` still ships via plugin skill discovery even though
`tools/package_skill.py` excludes it — decide whether external users should see it.

## Status

This repo replaced an earlier set of API docs that had drifted for nine months. The previous
content was removed rather than edited, because its quick start taught an authentication
path that silently dropped formulas. It remains in git history.

`PRE-PUBLIC-CHECKLIST.md` lists what must be true before this repo is published again.
