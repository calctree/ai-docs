# CalcTree GraphQL reference

Every operation the skill needs, with its variables and response shape. This file
exists so you can drive CalcTree with nothing but an HTTP client — no CalcTree
libraries, no Node, no Python. `scripts/calctree_api.py` is a convenience wrapper
around exactly these calls; if you can run it, prefer it, and read this when you
need the wire format.

- **Endpoint:** `POST https://graph.calctree.com/graphql`
- **Headers:** `Content-Type: application/json`, `x-api-key: <your key>`
- **Body:** `{"query": "<document>", "variables": { ... }}`

One API key covers every call below. An invalid or empty key comes back as a bare
`"Unexpected error."` with no 401 and no mention of auth — if you see that, check
the key before debugging anything else.

## The write path, in order

Creating a page that renders and computes is three calls. All three are required.

1. `createPageSync` — makes the page
2. `addPageNode` — registers it in the page tree, or it is orphaned and invisible
3. `insertMDXContent` — puts prose and calculation blocks in, and persists the statements

Then, until the platform fixes it, a fourth: `createOrUpdateCalculation` to set the
statement titles `insertMDXContent` drops. See **Statement titles** below.

## Ids

Client-minted ids are accepted for pages and statements; a UUID is fine.
Platform-generated ids are 21-character nanoids, so id shape is how you tell an
API-created page from a UI-created one. Nothing depends on it.

The **calculation id equals the page id**. There is no separate calculation to create.

## Reads

### pages — list a workspace

```graphql
query($workspaceId: ID!) {
  pages(workspaceId: $workspaceId) { id title }
}
```

Deleting a page is a **soft** delete, so trashed pages still come back here and
accumulate.

### page + pageContent — title and body

```graphql
query($workspaceId: ID!, $pageId: ID!) {
  page(workspaceId: $workspaceId, id: $pageId) { id title }
  pageContent(workspaceId: $workspaceId, pageId: $pageId) { content }
}
```

### calculation — the graph and its computed values

This is how you verify a page. `revisionId` is `"~"` for latest.

```graphql
query($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
  calculation(workspaceId: $workspaceId, calculationId: $calculationId, revisionId: $revisionId) {
    statements {
      statementId
      title
      engine
      formula
      namedValues { name value }
      errors
    }
  }
}
```

Variables: `{"workspaceId": "...", "calculationId": "<pageId>", "revisionId": "~"}`

`namedValues[].value` arrives **JSON-encoded as a string**, MathJS-serialised:

```json
"{\"mathjs\":\"Unit\",\"value\":8,\"unit\":\"m\",\"fixPrefix\":false}"
```

So parse it, then read `.value` and `.unit`. Plain numbers and strings come through
as themselves.

**Why `revisionId` is `"~"`:** revision ids are KSUIDs, and `~` sorts above every
base62 character, so it always means latest. Hex-looking values (`"ffffffff"`)
appear in older documentation and answer today only because no revision id has yet
sorted above them — a KSUID beginning with a letter after `f` silently stops
matching. Do not use a hex value.

**Evaluation is asynchronous.** Settle a couple of seconds after a write before
reading, or the read comes back with zero statements, or with statements that have
no `namedValues` yet.

### pageMDX — body back as MDX

```graphql
query($workspaceId: ID!, $pageId: ID!) {
  pageMDX(workspaceId: $workspaceId, pageId: $pageId)
}
```

**Never verify a calculation with this.** MDX serialisation round-trips prose
reliably but returns calculation blocks **empty**, so a perfectly good page looks
broken. Use the `calculation` query.

## Writes

### createPageSync

```graphql
mutation($workspaceId: ID!, $input: CreatePageInput!) {
  createPageSync(workspaceId: $workspaceId, input: $input) { id title }
}
```

```json
{"workspaceId": "<ws>",
 "input": {"id": "<uuid>", "title": "Beam check", "workspaceId": "<ws>", "parentId": "<optional>"}}
```

`workspaceId` appears both at the top level and inside `input`.

### addPageNode — required

```graphql
mutation($workspaceId: ID!, $input: AddPageNodeInput!) {
  addPageNode(workspaceId: $workspaceId, input: $input) { newPageId parentId }
}
```

```json
{"workspaceId": "<ws>", "input": {"pageId": "<pageId>", "parentId": "<optional>"}}
```

Skip this and the page exists but is invisible in the UI.

### insertMDXContent

```graphql
mutation($workspaceId: ID!, $pageId: ID!, $content: String!, $position: LocationInput!) {
  insertMDXContent(workspaceId: $workspaceId, pageId: $pageId, content: $content, position: $position) {
    insertedCount
    statementsCreated
  }
}
```

```json
{"workspaceId": "<ws>", "pageId": "<pageId>", "content": "<mdx>", "position": {"path": [0]}}
```

`position` is a Slate location. `{"path": [0]}` prepends; to append, pass the
current top-level node count.

**Check `statementsCreated` against the number of calculation blocks you sent.** A
write that inserted nodes and created zero statements is a failure whatever the HTTP
status says — that is the shape the old auth bug took, and it is worth keeping as a
tripwire.

Prose and calculation blocks both go through here, and the statements **do** evaluate
server-side. A separate `createOrUpdateCalculation` is not needed to make a page
compute.

### createOrUpdateCalculation

Writes the calculation graph only — no page body. Use it for graph-only writes, for
cross-page references, and to set titles.

```graphql
mutation($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!) {
  createOrUpdateCalculation(workspaceId: $workspaceId, calculationId: $calculationId, withStatements: $withStatements) {
    calculationId
    revisionId
  }
}
```

```json
{"workspaceId": "<ws>", "calculationId": "<pageId>",
 "withStatements": [{"statementId": "<uuid>", "title": "Beam moment",
                     "engine": "multiline_mathjs",
                     "formula": "span = 8 m\nload = 45 kN / m\nM_max = load * span^2 / 8"}]}
```

`engine` is one of `mathjs`, `multiline_mathjs`, `python`, `excel`, `dataset`,
`connection`. All statements in a calculation share one scope.

Reusing an existing `statementId` **updates in place**. This upsert never deletes,
so a wrong id leaves the old statement live and evaluating alongside the new one.

The returned `revisionId` can be `null` even on success. Do not depend on it; read
back with `"~"`.

Unlike `insertMDXContent`, this **does** set titles.

### deletePage

```graphql
mutation($workspaceId: ID!, $id: ID!) {
  deletePage(workspaceId: $workspaceId, id: $id) { __typename }
}
```

Soft delete.

## Statement titles

`insertMDXContent` carries the MDX `name` attribute to the document node but not
into the statement it creates, so every statement comes back titled
`"Untitled Statement"`. Values are unaffected; the cost is presentational.

To fix it, re-upsert each statement with the **same** `statementId` plus its title
via `createOrUpdateCalculation`.

Two traps, both of which the bundled script handles:

1. **Match statements to MDX blocks by the variables they define, not by order.**
   The graph does not come back in document order.
2. **The ids are not stable immediately.** Ids returned soon after
   `insertMDXContent` are not the ones the graph settles on, and upserting against
   a stale id is a *silent no-op*: it reports success, changes nothing, and leaves
   the page permanently untitled. Verified live on 2026-08-21 — two identical
   builds a minute apart, one titled everything, the next titled nothing and said
   it had succeeded. Waiting for `namedValues` to appear is not a sufficient guard.
   Read the ids, upsert, then **read back and confirm the titles are visible**, and
   retry with fresh ids if they are not.

## Cross-page references

A reference is a point-in-time snapshot of the source page's computed values,
written onto the target page as a `multiline_mathjs` statement whose object carries
a metadata key:

```
alias = {
  "span": 8 m,
  "M_max": 360 kN m,
  "__ct_meta": {"sourcePageId":"...","sourcePageTitle":"...","sourceWorkspaceId":"...","importedAt":"2026-08-21T07:38:59.586Z"}
}
```

The `__ct_meta` key is what promotes it into a real source-linked page reference
rather than a plain block. The alias derives from the source title with every
non-word character replaced by `_`. Values are re-serialised to mathjs source
(`{"mathjs":"Unit","value":8,"unit":"m"}` becomes `8 m`) so downstream formulas can
consume them.

Summary and roll-up pages should reference upstream results this way rather than
recomputing them.

## In-place edits

Content edits can append and update but **cannot remove or reorder** body nodes, and
updating content leaves the old statements in the calculation — so every variable
ends up defined twice and the page nulls out. To genuinely replace a page's content,
delete the page and create it again.
