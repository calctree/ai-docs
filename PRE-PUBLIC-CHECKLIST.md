# Before this repo goes public again

The repo was made private on 2026-07-30 pending this cleanup. It was previously public and
Context7-indexed. Nothing below blocks internal use: the workarounds are documented in
`SKILL.md` and we keep building against them.

## Blocker 1: `x-api-key` silently drops formula statements

**Fix server-side. Do not ship this as permanent public guidance.**

Under `Authorization: Bearer <jwt>`, a content write creates the body node and the
calculation statement together. Under `x-api-key`, the body node lands, the calculation
service rejects the forwarded key, and the statement never persists. The caller gets a 200
and a page that looks correct with empty calculation blocks. No error surfaces.

Why it matters for a public repo: an API key is the credential we would hand to an external
integrator, and it is the one that produces silently broken pages. Publishing "use Bearer,
never the API key" tells the world that our documented authentication path does not work for
the main write. The honest fix is for the calculation service to accept the forwarded API
key, or for the gateway to exchange it for a service token before forwarding.

### The workaround in effect, and what it costs

Every internal flow now mints a **Bearer token by logging in with an account email and
password held in env**: the harness via `scripts/auth.ts`, and the calctree-ops GraphQL proxy
via `server/routes/calctree.ts`. It works, and it stays until the platform fix lands, because
it is what unblocks template building.

**It is a deliberately temporary shape, and worse than an API key on four counts:**

1. **Scope.** An API key is issued for API access. A password is the credential for the whole
   account: it works in the web UI and can change account settings.
2. **Revocation.** Rotating a key is targeted. Rotating a password invalidates every session
   that account has, and breaks anything else using it, which includes the Playwright
   report-printing flow.
3. **Audit.** Writes appear as that account rather than as a service identity, so "the ops app
   did this" is indistinguishable from a person doing it in the browser.
4. **Least privilege.** A key can be scoped later. A password cannot be scoped at all.

Nothing about this is a design choice. It exists only because the API key does not work for
content writes.

**Narrowing steps. The first is DONE as of 2026-07-30:**

- **DONE.** The ops proxy sends Bearer only for `insertMDXContent` and
  `createOrUpdateCalculation`; everything else goes on `x-api-key`, so the account credential
  is off the great majority of traffic. Paired with a tripwire: a write that inserts nodes but
  creates zero statements is logged as an error, since a narrow allowlist would otherwise fail
  the same silent way the original bug did.
- Point ops at the eddie ops account. Note this is **not** only about the password: verified
  2026-07-30 that `CALCTREE_API_KEY` also resolves to a human account, so api-key writes are
  already attributed to a person. `CALCTREE_EDDIE_API_KEY` is already present in the ops env,
  so both the key and the login can move to the service account.

- **Exit condition:** an API key write creates the statement, verified by a live test. Then
  delete the login paths in `scripts/auth.ts` and `server/routes/calctree.ts`, remove the
  password from both envs, and rewrite `SKILL.md` section 1 to present the API key as the
  normal path.
- **Owner:** platform / tech team. Needs a ticket.

## Blocker 2: ID format guidance contradicts working practice

`API_REFERENCE.md` line 65 says "**CRITICAL:** CalcTree uses nanoid format for all IDs, NOT
UUIDs". Platform-generated ids are indeed 21-character nanoids, but the harness has been
creating pages with `crypto.randomUUID()` and they work. One of those is wrong, or the truth
is "client-minted ids of either shape are accepted", which is what we currently believe.
Settle it with a live test before either claim is published.

## Blocker 3: the latest-revision sentinel is ad-hoc everywhere

Revision ids are KSUIDs (`xksuid`, base62). The canonical sentinel for "latest" is
`REVISION_INFINITE = RevisionId('~')` in `calculations/packages/common/src/types.ts`, and `~`
is correct because it sorts above every base62 character.

Nothing else uses it. `calculations/packages/core/src/admin.ts` passes `'fffffff'` (seven f
characters), our harness passes `'ffffffffff'` (ten), and the old public docs told people to
use `'ffffffff'` (eight). None of those is safe: a KSUID beginning with any letter after `f`
sorts **above** them, so a hex-style sentinel silently stops meaning "latest" depending on
which revision id the platform happened to mint.

- **Needed:** confirm what the public GraphQL API accepts as the latest-revision sentinel,
  then say exactly that once. If `~` works through the gateway, publish `~` and fix the
  internal callers.
- **Do not publish a hex value.** The current context7 rule says as much and marks it
  untested.
- **Owner:** platform / tech team, plus a live test from our side.

## Blocker 4: stale content

Every doc here predates 2026-02 and none has been re-verified: `API_REFERENCE.md` (726 lines,
2025-11-08), `EXAMPLES.md` (904), `TROUBLESHOOTING.md` (437), `CALCULATION_GUIDE.md` (447),
`calctree_reference.py` (276), and `tests/` (45 exploration scripts, all 2025-11-08, no
runner). These get deleted or archived and replaced by `SKILL.md` plus the published harness
primitives. Publishing them as they stand is worse than publishing nothing, because the
quick start teaches Blocker 1.

Resolved 2026-07-30: `MDX_SYNTAX.md` and `PYTHON_GUIDE.md` were deleted. What was still true
was merged into the skill, verified against the engine and the converters rather than copied:
the `ct` surface, the pre-wrapped quantity trap, `.magnitude` being a property, the
`plot_prefix` default, the library list, and the component vocabulary actually in use.

## Blocker 5: repo identity

Rename to the convention for a published AI skillset, `calctree-skills` laid out as
`skills/calctree/SKILL.md`, plus `llms.txt` at the root. GitHub redirects the old URL, but
Context7 indexes by project name, so the rename and the Context7 re-point happen together.

## Not a blocker, but decide before publishing

Publishing the harness primitives publishes the shape of the write path: that a page must be
registered in the page tree or it is orphaned, that evaluation is async so reads need to
settle, that MDX round-trips prose but not calculation blocks. All fine to publish, all
better fixed than documented, and none of it stops the repo going out.
