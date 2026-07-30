---
name: calctree
description: Build and read CalcTree calculation pages programmatically via the GraphQL API. Use when creating engineering calculations, inserting MDX content with live formulas, reading computed values back, or linking pages together. Covers auth, the write path, MathJS and Python statements, and the rules that silently break pages.
---

# CalcTree

CalcTree is an engineering calculation platform. A **page** holds prose plus calculation
blocks; the blocks form a **calculation graph** that evaluates server-side, with real units.
This skill is how an AI agent drives it from outside the platform.

Everything here is verified working against the live API. Treat it as settled.

## 1. Auth: use Bearer, not an API key

Endpoint: `https://graph.calctree.com/graphql`, header `Authorization: Bearer <jwt>`.

Mint a token with `POST https://api.calctree.com/api/auth/login` with `{email, password}`,
which returns `{accessToken}`.

**Do not use `x-api-key` for content writes.** The API key does not carry through to the
calculation service, so `insertMDXContent` creates the body node while the statement is
rejected: you get a page that looks correct with empty calculation blocks and no error.
Bearer creates the node and the statement together.

## 2. The write path

Two calls, in order:

1. **Create the page and register it in the page tree.** Both are required. A page that
   exists but is not in the tree is orphaned and invisible in the UI. Client-minted ids are
   accepted; platform-generated ids are 21-character nanoids.
2. **`insertMDXContent(workspaceId, pageId, mdx, position)`** returns
   `{insertedCount, statementsCreated}`. Prose and inline calculation blocks both go through
   here. Always check `statementsCreated` matches what you sent.

For calculation-graph-only writes with no body node, use
`createOrUpdateCalculation(workspaceId, pageId, statements[])`, where each statement is
`{statementId?, title, engine, formula}` and `engine` is one of `mathjs`,
`multiline_mathjs`, `python`, `excel`, `dataset`, `connection`. Note that the calculation id
equals the page id.

## 3. MDX calculation syntax

Single assignment, self-closing:

```
<Assignment name="span" formula='span = 8 m' />
```

Multi-line block, surrounded by blank lines, with a bare fence inside:

```
<EquationBlock name="Beam moment">
```
span = 8 m
load = 45 kN / m
M_max = load * span^2 / 8
```
</EquationBlock>
```

No H1 in the body: the page title already renders as the heading.

## 4. Reading back and verifying

- **Settle about two seconds after a write before reading.** Evaluation is asynchronous
  server-side, and an immediate read can return zero statements.
- Read the graph and its values with the page-context query, which returns statements with
  `namedValues` and `errors`. Values arrive MathJS-serialised, for example
  `{mathjs: "Unit", value: 8, unit: "m"}`.
- **Do not verify calculations by reading the page back as MDX.** MDX serialisation
  round-trips prose reliably but returns calculation blocks empty, so a correct page looks
  broken. Use the page-context query.
- Calculations really do evaluate server-side. No browser is needed.

## 5. Formula rules

Same engine as the in-app editor:

- Assignment syntax always: `variable = expression`.
- Units on inputs (`load = 5 kN`); calculated values inherit them, so do not re-declare.
- `equalText()` for string comparison, not `==`. Word operators: `and`, `or`, `xor`, `not`.
- Double-quote strings.
- **Avoid variable names that collide with unit abbreviations** (`N`, `V`, `Pa`, `M`, `mm`,
  `m`, `s`, `kg`, `K`, `A`, `g`, `h`, `d`, `J`). Use `M_max`, not `M`. A variable named `mm`
  shadows the millimetre unit and nulls every later conversion on the page.
- Within one `multiline_mathjs` formula, define a variable before using it. Across separate
  statements order does not matter: it is a dependency graph.

## 6. Writing pages that read correctly

The API will happily create a page that computes but presents badly. These are the ones that
bite:

- **Let units flow.** A dimensional value carries its unit and prints it, so never write the
  unit into a column heading and never strip a value to a bare number to do so. Convert for
  display with `to` (`As_r = (round(As / (1 mm^2), 0) * (1 mm^2)) to mm^2`); without the `to`
  MathJS auto-rescales and mm² becomes ha. `round()` on a unitful value must strip the unit
  first: `round(X / (1 mm), 3)`.
- **Round for display in a separate copy**, never on the value the rest of the calculation
  consumes.
- **A pass/fail check must be a named boolean**, never a string ternary.
  `check = util <= 1 ? "PASS" : "FAIL"` is always truthy, so a traffic-light chip renders
  green whatever the result. Write `within_limits = util <= 1` and name the variable so it
  reads as the verdict.
- **Mentions are display-only.** Do the rounding in MathJS and treat the mention as a
  read-out. A mention of a variable the page never defines renders as the word `undefined`
  and no check will catch it, so every mention key must resolve. Text placed immediately
  after a mention inside a table cell is dropped: put the unit in a separate column.
- **Charts** need four things together or you get an untitled node and no image: a named
  Python block, a bare fence rather than a language-tagged one, a plot prefix set before
  `plt.show()`, and an image mention immediately above the block. Any name that renders as a
  label needs a leading underscore and underscores between words; hyphens render as minus
  signs and literal spaces are dropped.
- **Escape `<` and `>` as `&lt;` and `&gt;` everywhere**, prose included. A raw one truncates
  the import from that point on.
- **Never put an offset unit (`degC`, `degF`) in scope on a page with a Python cell.** One
  such value fails the whole cell with "Ambiguous operation with offset unit".
- Multi-branch categorical results belong in Python plus a table, not a nested ternary.

## 7. Linking pages

A cross-page reference is a snapshot of the source page's computed values, created as a
`multiline_mathjs` statement whose object carries a metadata key alongside the values. That
metadata key is what makes it a source-linked page reference rather than a plain block.
Summary and roll-up pages should **reference** upstream results, not recompute them.

## 8. Gotchas worth knowing before you start

- Deleting a page is a **soft** delete. Trashed pages still come back from the pages query
  and accumulate, which slows workspace sync.
- In-place content edits can append and update but **cannot remove or reorder** body nodes,
  and updating content leaves the old statements in the calculation, so every variable ends
  up defined twice and the page nulls out. To genuinely replace a page's content, delete the
  page and re-create it.
- Do not rely on visibility flags to hide a block. Identical MDX has imported hidden on some
  pages and visible on others.
- A traffic light must sit one hop from the block that computes its input. A chip whose
  formula reads a variable derived in a later block resolves to null.
