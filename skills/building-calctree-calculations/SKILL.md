---
name: building-calctree-calculations
description: Build and read CalcTree calculation pages programmatically via the GraphQL API. Use when creating engineering calculations, inserting MDX content with live formulas, reading computed values back, or linking pages together. Covers auth, the write path, MathJS and Python statements, and the rules that silently break pages.
---

# CalcTree

CalcTree is an engineering calculation platform. A **page** holds prose plus calculation
blocks; the blocks form a **calculation graph** that evaluates server-side, with real units.
This skill is how an AI agent drives it from outside the platform.

Everything here is verified working against the live API. Treat it as settled.

## Bundled code

The primitives implement everything below. Prefer running them over re-writing the calls.

- `scripts/calctree-api.ts` — page creation with tree registration, MDX insert, calculation
  writes, page-context reads, cross-page references. **Read as reference** when you need the
  exact GraphQL shape; **import and call** when driving.
- `scripts/auth.ts` — `ensureBearer()`. Requires `CALCTREE_LOGIN_EMAIL` and
  `CALCTREE_LOGIN_PASSWORD`, or a pre-set `CALCTREE_BEARER`.
- `examples/smoke-two-page.ts` — **run this first** to confirm your credentials and endpoint
  work end to end. It creates two linked pages, reads the computed values back, and prints the
  page URLs:

  ```bash
  npx tsx examples/smoke-two-page.ts <workspaceId>
  ```

Requires `tsx` (or any TypeScript-aware runner). No other dependencies.

## 1. Auth: use Bearer, not an API key

Endpoint: `https://graph.calctree.com/graphql`, header `Authorization: Bearer <jwt>`.

Mint a token with `POST https://api.calctree.com/api/auth/login` with `{email, password}`,
which returns `{accessToken}`.

**Do not use `x-api-key` for content writes.** The API key does not carry through to the
calculation service, so `insertMDXContent` creates the body node while the statement is
rejected: you get a page that looks correct with empty calculation blocks and no error.
Bearer creates the node and the statement together.

This is a known platform limitation rather than the intended design. When it is fixed, the API
key becomes the normal path for every call and this section changes accordingly. Until then, the API key is
fine for reads and for every other mutation; only `insertMDXContent` and
`createOrUpdateCalculation` need a login-minted Bearer. Either way, **check the response**: a
write that returns zero created statements has failed, whatever the HTTP status says.

## 2. The write path

Three calls, in order:

1. **Create the page and register it in the page tree.** Both are required. A page that
   exists but is not in the tree is orphaned and invisible in the UI. Client-minted ids are
   accepted; platform-generated ids are 21-character nanoids.
2. **`insertMDXContent(workspaceId, pageId, mdx, position)`** returns
   `{insertedCount, statementsCreated}`. Prose and inline calculation blocks both go through
   here. Always check `statementsCreated` matches what you sent.

3. **`applyMdxStatementTitles(workspaceId, pageId, mdx)`** — set the statement
   titles, which step 2 does not do. `insertMDXContent` sends the MDX `name`
   attribute to the document node but not to the calculation graph, so every
   statement comes back titled "Untitled Statement". Verified 2026-08-21 against
   all four naming forms (`<Assignment name>`, `<EquationBlock name formula="...">`,
   the canonical `<EquationBlock name>` plus fenced block, and `<Python name>`) —
   every one lost the title, so this is not a quirk of the older attribute form.
   The values are unaffected; the cost is presentational, and it is what makes a
   Python node read as "Untitled". The helper re-upserts each statement with the
   SAME `statementId` plus its title, matching statements to MDX blocks by the
   variables they define rather than by order, because the graph does not come
   back in document order. Reusing the id updates in place — verified no
   duplication, which matters because this upsert never deletes, so a wrong id
   leaves the old statement live and evaluating beside the new one.

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

## 7. Python statements

A `python` engine statement runs server-side with two globals injected, `ct` and `ctconfig`.
The full surface, from the engine:

| | |
|---|---|
| `ct.quantity` | pint `Quantity`. `force = ct.quantity("1 N")` |
| `ct.units` | the pint `UnitRegistry`. `kN = ct.units("kN")` |
| `ct.open` | read or write a file attached to the page: `ct.open('data.csv', mode='r')` |
| `ct.page_files` | presigned URLs for the page's files |
| `ct.keep_file` | persist a file back to the page |
| `ct.keep_dataframe`, `ct.load_dataframe` | persist and reload a dataframe between runs |
| `ctconfig.plot_prefix` | the prefix used to name emitted plot images |

Units, and the mistake everyone makes:

- **MathJS variables with units arrive already wrapped as `ct.quantity` objects. Do not wrap
  them again.** Referencing `V_Ed` from the page scope gives you a pint quantity, not a float.
- Create new ones with `ct.quantity("100 kN")`. Arithmetic across units works:
  `force / area` gives a pressure.
- Convert with `.to('unit')`. Read the number with **`.magnitude`, which is a property, not a
  method**: `.magnitude` not `.magnitude()`.
- pint raises on incoherent operations, so adding a length to a time fails loudly. That is
  intended.
- **Never put an offset unit (`degC`, `degF`) in scope on a page with a Python cell.** One such
  value fails the entire cell with "Ambiguous operation with offset unit".

Plots:

- `ctconfig.plot_prefix` is **pre-set per statement** to `ct_plot_<statementId>_`, which you
  cannot predict when authoring MDX. So set your own (`ctconfig.plot_prefix = "beam"`) and
  reference the first image as `beam1`, otherwise the image mention cannot resolve.
- End with `plt.show()`. A bare `fig` emits nothing.

Only libraries pre-installed in the environment can be imported; imports are checked before
execution. The engineering set includes `numpy`, `pandas`, `scipy`, `sympy`, `matplotlib`,
`seaborn`, `pint`, `handcalcs`, `sectionproperties`, `concreteproperties`, `structuralcodes`,
`steelpy`, `anastruct`, `beambending`, `indeterminatebeam`, `pycba`, `pynitefea`, `openseespy`,
`opsvis`, `pycufsm`, `pycalculix`, `compas`, `ezdxf`, `shapely` via `cad-to-shapely`, `gempy`,
`groundhog`, `pygef`, `fluids`, `thermo`, `ht`, `fipy`, `nutils`, `duckdb`, `pyarrow`,
`openpyxl`, `scikit-learn`, `pymc`, `arviz`, `specklepy`, `blue-prints`.

## 8. The MDX component vocabulary

Calculation content is MDX. The components you will actually use:

| Component | Purpose |
|---|---|
| `<Assignment>` | one named formula |
| `<EquationBlock>` | several formulas in one block |
| `<Python>` | a Python statement, needs a `name` or the node shows as "Untitled" |
| `<Mention>` | display a computed value, an image, or a traffic-light chip |
| `<TrafficLights>` | the pass/fail chip, driven by a named boolean |
| `<MatrixBlock>` | matrix input and output |
| `<SimpleInput>`, `<SelectInput>`, `<RadioInput>` | interactive inputs |
| `<RichTable>` | a table whose cells hold components; plain GFM pipe tables otherwise |

## 9. Linking pages

A cross-page reference is a snapshot of the source page's computed values, created as a
`multiline_mathjs` statement whose object carries a metadata key alongside the values. That
metadata key is what makes it a source-linked page reference rather than a plain block.
Summary and roll-up pages should **reference** upstream results, not recompute them.

## 10. Gotchas worth knowing before you start

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
- `insertMDXContent` does create the calculation statements — a separate
  `createOrUpdateCalculation` is not needed to make a page compute — but it does not
  set their titles. See section 2, step 3.
- Client-minted UUIDs are accepted for page and statement ids, so pages you create
  this way have UUID ids while platform-created pages have 21-character nanoids.
  Nothing depends on the shape, but it is how you tell them apart in a workspace.
