/**
 * Two-page smoke test against a SANDBOX workspace. Proves the Tier-1 driving
 * layer end-to-end AND exercises the cross-page read/reference path (PRs #264/#266):
 *   1. create page A (+tree), give it inputs + a derived result
 *   2. read A back (getPageContext) — does an API-created calc evaluate server-side?
 *   3. create page B (+tree)
 *   4. reference A into B (API-native snapshot of A's values)
 *   5. read B back, print everything + the /edit URLs
 *
 * Usage: CALCTREE_API_KEY=... tsx harness/smoke-two-page.ts <workspaceId>
 */
import {
  createPageInTree, insertMDXContent, getPageContext, referencePageViaApi,
} from './calctree-api.ts'
import { ensureBearer } from './auth.ts'

const ws = process.argv[2]
if (!ws) { console.error('usage: tsx harness/smoke-two-page.ts <workspaceId>'); process.exit(1) }
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

await ensureBearer()
console.log('authenticated (Bearer)\n')
const url = (id: string) => `https://app.calctree.com/edit/${ws}/${id}`
const fmtVal = (raw: unknown): string => {
  let v: unknown = raw
  if (typeof v === 'string') { try { v = JSON.parse(v) } catch { return String(raw) } }
  if (v && typeof v === 'object' && (v as { mathjs?: string }).mathjs === 'Unit') {
    const u = v as { value: number; unit: string }; return `${u.value} ${u.unit}`
  }
  return JSON.stringify(v)
}
const show = (label: string, ctx: Awaited<ReturnType<typeof getPageContext>>) => {
  console.log(`  ${label}: ${ctx.statements.length} statements`)
  for (const s of ctx.statements) {
    const vals = s.namedValues.filter((v) => v.name).map((v) => `${v.name}=${fmtVal(v.value)}`).join(', ')
    const errs = s.errors?.length ? `  ERRORS: ${JSON.stringify(s.errors)}` : ''
    console.log(`    [${s.engine}] ${s.formula.replace(/\n/g, ' ')}${vals ? `  => ${vals}` : '  (no value)'}${errs}`)
  }
}

// 1. Page A with inputs + derived result
const A = await createPageInTree(ws, 'Smoke A — inputs')
console.log(`created A: ${url(A.id)}`)
// Bearer path: prose AND formula go through insertMDXContent. The EquationBlock carries
// the formula, so the body node + persisted statement are created together (renders + computes).
// No leading '#' — the page title already renders as the H1.
const mdxA = [
  'Simply-supported beam: UDL over a clear span, mid-span moment.', '',
  '<EquationBlock name="Beam moment">', '```', 'span = 8 m', 'load = 45 kN / m', 'M_max = load * span^2 / 8', '```', '</EquationBlock>', '',
].join('\n')
const insA = await insertMDXContent(ws, A.id, mdxA)
console.log(`  A via insertMDXContent: ${insA.insertedCount} nodes, ${insA.statementsCreated} statements`)

// 2. read A back (settle first — statements evaluate async)
await sleep(2000)
const a = await getPageContext(ws, A.id)
show('page A', a)

// 3. Page B
const B = await createPageInTree(ws, 'Smoke B — references A')
console.log(`\ncreated B: ${url(B.id)}`)
await insertMDXContent(ws, B.id, 'Pulls a point-in-time snapshot of page A’s values (a Nodes-panel linked-page card, by design).')

// 4. reference A into B (stays a calc-graph "Page:" card — correct, not a body block)
const ref = await referencePageViaApi(ws, B.id, A.id)
console.log(`  referencePageViaApi -> alias="${ref.alias}", ${ref.count} values snapshotted`)

// 5. read B back (settle first)
await sleep(2000)
const b = await getPageContext(ws, B.id)
show('page B', b)

console.log(`\nDONE.\n  A: ${url(A.id)}\n  B: ${url(B.id)}`)
