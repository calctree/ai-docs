/**
 * Tier-1 CalcTree driving primitives: everything reachable over the production
 * GraphQL mesh with an `x-api-key` (no browser). Query/mutation shapes copied
 * verbatim from pages/services/page-service (pageContextClient.ts + schema.graphql)
 * so this exercises PR #264's exact read path.
 *
 * Browser-only ops (add/eval a statement, cross-page reference snapshot) are NOT
 * here — they live in the Playwright layer (Tier 2).
 *
 * Env: CALCTREE_BEARER or CALCTREE_LOGIN_EMAIL/PASSWORD (required for content
 * writes — see authHeaders), CALCTREE_API_KEY (reads), CALCTREE_GRAPH_URL
 * (default prod mesh).
 */
const GRAPH_URL = process.env.CALCTREE_GRAPH_URL || 'https://graph.calctree.com/graphql'
// '~' is the canonical latest-revision sentinel (REVISION_INFINITE in
// calculations/packages/common/src/types.ts) and is correct because '~' sorts above every
// base62 character, so it always means "latest". Verified 2026-08-21 that the public gateway
// accepts it. The hex values in circulation ('fffffff', 'ffffffff', 'ffffffffff') also answer
// today, but only because no revision id has yet sorted above them: a KSUID beginning with any
// letter after 'f' silently stops matching. Do not go back to a hex value.
const LATEST_REVISION_ID = '~'

/**
 * Auth: prefer a Bearer user token (CALCTREE_BEARER) over x-api-key. Bearer is
 * REQUIRED for body-rendered calcs — under x-api-key, insertMDXContent's forwarded
 * key is rejected by the calc-service so MDX-embedded formulas silently drop.
 */
function authHeaders(): Record<string, string> {
  const bearer = process.env.CALCTREE_BEARER
  if (bearer) return { Authorization: `Bearer ${bearer}` }
  const k = process.env.CALCTREE_API_KEY
  if (k) return { 'x-api-key': k }
  throw new Error('Set CALCTREE_BEARER (preferred) or CALCTREE_API_KEY')
}

/** Mint a Bearer access token via the monolith auth endpoint. `apiBase` e.g. https://api.calctree.com/api */
export async function login(apiBase: string, email: string, password: string): Promise<string> {
  const res = await fetch(`${apiBase.replace(/\/$/, '')}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const j = (await res.json().catch(() => ({}))) as { accessToken?: string; message?: string }
  if (!j.accessToken) throw new Error(`login failed (HTTP ${res.status}): ${j.message ?? JSON.stringify(j).slice(0, 160)}`)
  return j.accessToken
}

async function gql<T>(query: string, variables: Record<string, unknown>): Promise<T> {
  const res = await fetch(GRAPH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ query, variables }),
  })
  const json = (await res.json()) as { data?: T; errors?: { message: string }[] }
  if (json.errors?.length) throw new Error(`GraphQL: ${json.errors.map((e) => e.message).join('; ')}`)
  if (!json.data) throw new Error(`No data (HTTP ${res.status})`)
  return json.data
}

/** Mint a UUID for new page / statement ids (per the CalcTree content-API guide). */
export function newId(): string {
  return crypto.randomUUID()
}

// ---- READ (PR #264 path) ----

export type WorkspacePage = { id: string; title: string }
export async function listWorkspacePages(workspaceId: string): Promise<WorkspacePage[]> {
  const d = await gql<{ pages: WorkspacePage[] }>(
    `query($workspaceId: ID!){ pages(workspaceId: $workspaceId){ id title } }`,
    { workspaceId },
  )
  return d.pages ?? []
}

export type PageStatement = {
  statementId: string
  title: string | null
  engine: string
  formula: string
  namedValues: { name: string | null; value: unknown }[]
  errors?: unknown[]
}
export type PageContext = {
  page: { id: string; title: string } | null
  content: unknown
  statements: PageStatement[]
}
export async function getPageContext(workspaceId: string, pageId: string): Promise<PageContext> {
  const [contentD, calcD] = await Promise.all([
    gql<{ page: { id: string; title: string } | null; pageContent: { content: unknown } | null }>(
      `query($workspaceId: ID!, $pageId: ID!){
         page(workspaceId: $workspaceId, id: $pageId){ id title }
         pageContent(workspaceId: $workspaceId, pageId: $pageId){ content }
       }`,
      { workspaceId, pageId },
    ).catch(() => ({ page: null, pageContent: null })),
    gql<{ calculation: { statements: PageStatement[] } | null }>(
      `query($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!){
         calculation(workspaceId: $workspaceId, calculationId: $calculationId, revisionId: $revisionId){
           statements { statementId title engine formula namedValues { name value } errors }
         }
       }`,
      { workspaceId, calculationId: pageId, revisionId: LATEST_REVISION_ID },
    ).catch(() => ({ calculation: null })),
  ])
  return {
    page: contentD.page,
    content: contentD.pageContent?.content ?? null,
    statements: calcD.calculation?.statements ?? [],
  }
}

// ---- CREATE (page shell + tree registration; both accept api-key auth) ----

export type CreatedPage = { id: string; title: string }
export async function createPageSync(
  workspaceId: string,
  input: { id?: string; title: string; parentId?: string },
): Promise<CreatedPage> {
  const id = input.id ?? newId()
  const d = await gql<{ createPageSync: CreatedPage }>(
    `mutation($workspaceId: ID!, $input: CreatePageInput!){
       createPageSync(workspaceId: $workspaceId, input: $input){ id title }
     }`,
    { workspaceId, input: { id, title: input.title, workspaceId, ...(input.parentId ? { parentId: input.parentId } : {}) } },
  )
  return d.createPageSync
}

/** REQUIRED after createPageSync, else the page is orphaned/invisible in the tree. */
export async function addPageNode(
  workspaceId: string,
  input: { pageId: string; parentId?: string },
): Promise<{ newPageId: string; parentId: string | null }> {
  const d = await gql<{ addPageNode: { newPageId: string; parentId: string | null } }>(
    `mutation($workspaceId: ID!, $input: AddPageNodeInput!){
       addPageNode(workspaceId: $workspaceId, input: $input){ newPageId parentId }
     }`,
    { workspaceId, input },
  )
  return d.addPageNode
}

/** Convenience: create a page AND register it in the tree in one call. */
export async function createPageInTree(
  workspaceId: string,
  title: string,
  parentId?: string,
): Promise<CreatedPage> {
  const page = await createPageSync(workspaceId, { title, parentId })
  await addPageNode(workspaceId, { pageId: page.id, ...(parentId ? { parentId } : {}) })
  return page
}

// ---- CONTENT (MDX → page body + calc nodes; the prod-prompt-native path) ----

/**
 * Put the page's document body as MDX. Server-side `deserializeMd` turns MDX
 * components (<Assignment>, <EquationBlock>, <Python>) into calculation nodes in
 * the page's YJS doc — so this is the native pipe for the MDX our agent emits
 * (the prod system prompt is built to produce exactly this).
 *
 * NOTE: `createOrUpdateCalculation` below writes ONLY the calculation graph (no
 * page body). Use putInitialPageContent for a real, rendered page.
 *
 * CONFIRMED 2026-08-21 on a live run: MDX calc components inserted this way DO
 * register statements in the calculation graph and evaluate server-side, so a
 * separate createOrUpdateCalculation is not needed to make a page compute. What
 * it IS needed for is statement titles — see applyMdxStatementTitles.
 */
export async function putInitialPageContent(
  workspaceId: string,
  pageId: string,
  mdx: string,
): Promise<void> {
  await gql<{ putInitialPageContent: string }>(
    `mutation($workspaceId: ID!, $input: PutPageContentInput!){
       putInitialPageContent(workspaceId: $workspaceId, input: $input)
     }`,
    { workspaceId, input: { pageId, content: mdx } },
  )
}

/**
 * Insert MDX at a position in an existing page (the incremental/append path the
 * AI's `insertContent` tool uses). Returns how many doc nodes and calc statements
 * were created. `position` is a Slate LocationInput (@oneOf); default prepends at
 * `[0]`. To append, pass `{ path: [<current top-level node count>] }`.
 */
export async function insertMDXContent(
  workspaceId: string,
  pageId: string,
  mdx: string,
  position: { path: number[] } = { path: [0] },
): Promise<{ insertedCount: number; statementsCreated: number }> {
  const d = await gql<{ insertMDXContent: { insertedCount: number; statementsCreated: number } }>(
    `mutation($workspaceId: ID!, $pageId: ID!, $content: String!, $position: LocationInput!){
       insertMDXContent(workspaceId: $workspaceId, pageId: $pageId, content: $content, position: $position){
         insertedCount statementsCreated
       }
     }`,
    { workspaceId, pageId, content: mdx, position },
  )
  return d.insertMDXContent
}

/** Delete a page (soft-delete; also removes it from the tree). */
export async function deletePage(workspaceId: string, pageId: string): Promise<void> {
  await gql<{ deletePage: unknown }>(
    `mutation($workspaceId: ID!, $id: ID!){ deletePage(workspaceId: $workspaceId, id: $id){ __typename } }`,
    { workspaceId, id: pageId },
  )
}

/** Read a page's body back AS MDX (cleaner than Slate JSON for agent context / verification). */
export async function pageMDX(workspaceId: string, pageId: string): Promise<string | null> {
  const d = await gql<{ pageMDX: string | null }>(
    `query($workspaceId: ID!, $pageId: ID!){ pageMDX(workspaceId: $workspaceId, pageId: $pageId) }`,
    { workspaceId, pageId },
  )
  return d.pageMDX
}

// ---- CALCULATIONS (calc graph only — same path as push_awatif.ts) ----

export type StatementInput = {
  statementId?: string
  title: string
  formula: string
  /** 'mathjs' | 'multiline_mathjs' | 'python' | 'excel' | 'dataset' | 'connection' */
  engine: string
}

/** Add/replace statements on a page's calculation (calculationId === pageId). */
export async function createOrUpdateCalculation(
  workspaceId: string,
  pageId: string,
  statements: StatementInput[],
): Promise<{ calculationId: string; revisionId: string | null }> {
  const withStatements = statements.map((s) => ({
    statementId: s.statementId ?? newId(),
    formula: s.formula,
    title: s.title,
    engine: s.engine,
  }))
  const d = await gql<{ createOrUpdateCalculation: { calculationId: string; revisionId: string | null } }>(
    `mutation($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!){
       createOrUpdateCalculation(workspaceId: $workspaceId, calculationId: $calculationId, withStatements: $withStatements){
         calculationId revisionId
       }
     }`,
    { workspaceId, calculationId: pageId, withStatements },
  )
  return d.createOrUpdateCalculation
}

/** A named value from getPageContext arrives JSON-encoded; turn it into mathjs source. */
function valueToMathjsSource(raw: unknown): string {
  let v: unknown = raw
  if (typeof v === 'string') {
    try { v = JSON.parse(v) } catch { return JSON.stringify(raw) }
  }
  if (v && typeof v === 'object' && (v as { mathjs?: string }).mathjs === 'Unit') {
    const u = v as { value: number; unit: string }
    return `${u.value} ${u.unit}`
  }
  if (typeof v === 'number') return String(v)
  return JSON.stringify(v)
}

/**
 * API-native reproduction of PR #266's `referencePage`: read the source page's
 * current named values and write them onto the target page as a point-in-time
 * `multiline_mathjs` snapshot `alias = { name: <mathjs value>, ... }` via
 * createOrUpdateCalculation (formulas MUST go through the calc engine, never
 * insertMDXContent — under x-api-key the MDX path silently drops formulas).
 *
 * Values are re-serialized to mathjs source (Unit -> "8 m") so downstream formulas
 * can use them. This bypasses the frontend's @calctree/mathjs serializer, so it is
 * faithful for numeric/unit values and best-effort for exotic types. To test #266's
 * ACTUAL frontend path (createPageCalculationImport), drive the tim/ctp-4117 FE via
 * Playwright instead.
 */
export async function referencePageViaApi(
  workspaceId: string,
  targetPageId: string,
  sourcePageId: string,
  alias?: string,
): Promise<{ alias: string; statementId: string; count: number }> {
  const src = await getPageContext(workspaceId, sourcePageId)
  const title = src.page?.title ?? 'page'
  // alias derivation matches the FE: each non-word char -> '_' ("Smoke A — inputs" -> "Smoke_A___inputs")
  const a = alias ?? title.replace(/\W/g, '_')
  const entries = src.statements
    .flatMap((s) => s.namedValues)
    .filter((v) => v.name)
    .map((v) => `  ${JSON.stringify(v.name)}: ${valueToMathjsSource(v.value)}`)
  // The "__ct_meta" key is what promotes a multiline_mathjs statement into a
  // proper "Page"-type reference node (with a Source link), not a plain block.
  const meta = { sourcePageId, sourcePageTitle: title, sourceWorkspaceId: workspaceId, importedAt: new Date().toISOString() }
  entries.push(`  "__ct_meta": ${JSON.stringify(meta)}`)
  const formula = `${a} = {\n${entries.join(',\n')}\n}`
  const statementId = newId()
  await createOrUpdateCalculation(workspaceId, targetPageId, [
    { statementId, title: `Page: ${a}`, formula, engine: 'multiline_mathjs' },
  ])
  return { alias: a, statementId, count: entries.length - 1 }
}

export { GRAPH_URL }

// ---- STATEMENT TITLES (insertMDXContent does not carry MDX `name` through) ----

/**
 * `insertMDXContent` creates the statement but leaves its title "Untitled
 * Statement": the MDX `name` attribute reaches the document node, not the
 * calculation graph. Verified 2026-08-21 against all four naming forms
 * (`<Assignment name>`, `<EquationBlock name formula="...">`, the canonical
 * `<EquationBlock name>` + fenced block, and `<Python name>`) — every one came
 * back untitled, so this is not a quirk of the older attribute form.
 *
 * Untitled statements compute correctly; the cost is presentational (the drawer,
 * the statement list, and anything reading a node's name).
 *
 * The fix is a third call: re-upsert each statement with the SAME statementId
 * plus the title. Reusing the id updates in place — verified no duplication,
 * which matters because this upsert never deletes, so a wrong id would leave the
 * old statement live and evaluating alongside the new one.
 */
export type MdxBlock = { component: string; name: string; assigns: string[] }

const TITLED_COMPONENTS =
  'Assignment|EquationBlock|Python|SelectInput|RadioInput|SimpleInput|MatrixBlock|TrafficLights'

/** Pull `name` plus the variables each block assigns, in document order. */
export function parseMdxBlocks(mdx: string): MdxBlock[] {
  const re = new RegExp(
    `<(${TITLED_COMPONENTS})\\b([\\s\\S]*?)(?:\\/>|>([\\s\\S]*?)<\\/\\1>)`,
    'g',
  )
  const out: MdxBlock[] = []
  for (const m of mdx.matchAll(re)) {
    const [, component, attrs = '', inner = ''] = m
    const name = /\bname\s*=\s*"([^"]*)"/.exec(attrs)?.[1]
    if (!name) continue
    // formula can be an attribute (entity-encoded newlines) or a fenced block inside
    const attrFormula = /\bformula\s*=\s*(?:"([^"]*)"|'([^']*)')/.exec(attrs)
    const fenced = /```[a-z]*\n([\s\S]*?)```/.exec(inner)
    const src = (attrFormula?.[1] ?? attrFormula?.[2] ?? fenced?.[1] ?? '')
      .replace(/&#10;/g, '\n')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
    const assigns = src
      .split('\n')
      .map((l) => /^\s*([A-Za-z_]\w*)\s*=(?!=)/.exec(l)?.[1])
      .filter((v): v is string => Boolean(v))
    out.push({ component, name, assigns })
  }
  return out
}

/**
 * Set statement titles on a page from the `name` attributes in the MDX that
 * built it. Statements are matched to blocks by which variables they define,
 * not by order, because the calculation graph does not come back in document
 * order. Call it after `insertMDXContent` has settled.
 */
export async function applyMdxStatementTitles(
  workspaceId: string,
  pageId: string,
  mdx: string,
): Promise<{ titled: number; unmatched: string[]; untitledLeft: number }> {
  const blocks = parseMdxBlocks(mdx).filter((b) => b.assigns.length > 0)
  const ctx = await getPageContext(workspaceId, pageId)
  const used = new Set<string>()
  const updates: StatementInput[] = []

  for (const s of ctx.statements) {
    const names = new Set((s.namedValues ?? []).map((v) => v.name).filter(Boolean) as string[])
    let best: { block: MdxBlock; score: number } | null = null
    for (const block of blocks) {
      if (used.has(block.name)) continue
      const score = block.assigns.filter((a) => names.has(a)).length
      if (score > 0 && (!best || score > best.score)) best = { block, score }
    }
    if (!best) continue
    used.add(best.block.name)
    updates.push({
      statementId: s.statementId,
      title: best.block.name,
      formula: s.formula,
      engine: s.engine,
    })
  }

  if (updates.length) await createOrUpdateCalculation(workspaceId, pageId, updates)
  return {
    titled: updates.length,
    unmatched: blocks.filter((b) => !used.has(b.name)).map((b) => b.name),
    untitledLeft: ctx.statements.length - updates.length,
  }
}
