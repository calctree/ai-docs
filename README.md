# calctree-skills

The single source of truth for driving [CalcTree](https://www.calctree.com) programmatically:
the rules an AI agent needs, and the working primitives that implement them.

CalcTree is an engineering calculation platform. A **page** holds prose plus calculation
blocks; the blocks form a **calculation graph** that evaluates server-side with real units.

## Layout

```
skills/building-calctree-calculations/
  SKILL.md                    the skill: read this first
  scripts/calctree-api.ts     pages, MDX content, calculations, page references
  examples/                   end-to-end example
evals/                        three evaluation scenarios
llms.txt                      machine-readable index
```

## Quick start

```bash
export CALCTREE_API_KEY=...
npx tsx skills/building-calctree-calculations/examples/smoke-two-page.ts <workspaceId>
```

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
