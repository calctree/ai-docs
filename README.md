# calctree-skills

The single source of truth for driving [CalcTree](https://www.calctree.com) programmatically:
the rules an AI agent needs, and the working primitives that implement them.

CalcTree is an engineering calculation platform. A **page** holds prose plus calculation
blocks; the blocks form a **calculation graph** that evaluates server-side with real units.

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


## Quick start

```bash
export CALCTREE_API_KEY=...
python3 skills/building-calctree-calculations/examples/smoke_two_page.py <workspaceId>
```

No install: standard library only, no pip, no Node. The smoke test writes two real pages, so
point it at a workspace you do not mind writing to.

## Installing it

| Surface | How |
|---|---|
| Claude Code | `/plugin marketplace add calctree/calctree-skills` then `/plugin install calctree@calctree`, or copy the skill folder into `~/.claude/skills/` |
| claude.ai, desktop, Cowork | `python3 tools/package_skill.py`, then upload `dist/*.zip` under Settings > Features |
| Claude API | the same zip via `POST /v1/skills`. Note that surface has no network access, so only the guidance is usable there, not the write path |
| Cursor, Codex, other agent tools | point them at `AGENTS.md` |

Network access is required for everything except reading the guidance. On claude.ai, Free/Pro/Max
users toggle it in settings; Team and Enterprise admins allowlist `graph.calctree.com`.

Three things that catch everyone out, all covered in the skill:

1. **A page must be registered in the page tree.** A page that exists but is not in the tree
   is orphaned and invisible.
2. **Evaluation is asynchronous.** Settle about two seconds after a write before reading, or
   you may read zero statements.
3. **An invalid API key does not say so.** It comes back as a GraphQL `"Unexpected error."`
   with no 401 and no mention of auth.

## Status

This repo replaced an earlier set of API docs that had drifted for nine months. The previous
content was removed rather than edited, because its quick start taught an authentication
path that silently dropped formulas. It remains in git history.

`PRE-PUBLIC-CHECKLIST.md` lists what must be true before this repo is published again.
