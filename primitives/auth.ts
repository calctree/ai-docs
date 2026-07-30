/**
 * Mint a Bearer token for the CalcTree API.
 *
 * Bearer is required for content writes that carry formulas. See
 * skills/calctree/SKILL.md section 1: under `x-api-key` the body node is created
 * but the calculation statement is rejected, so the page looks correct and does
 * not compute.
 *
 * Env:
 *   CALCTREE_BEARER          use this token as-is and skip login
 *   CALCTREE_API_BASE        default https://api.calctree.com/api
 *   CALCTREE_LOGIN_EMAIL
 *   CALCTREE_LOGIN_PASSWORD
 */
import { login } from './calctree-api.ts'

export async function ensureBearer(): Promise<string> {
  if (process.env.CALCTREE_BEARER) return process.env.CALCTREE_BEARER

  const apiBase = process.env.CALCTREE_API_BASE || 'https://api.calctree.com/api'
  const email = process.env.CALCTREE_LOGIN_EMAIL
  const password = process.env.CALCTREE_LOGIN_PASSWORD

  if (!email || !password) {
    throw new Error(
      'Set CALCTREE_BEARER, or CALCTREE_LOGIN_EMAIL and CALCTREE_LOGIN_PASSWORD'
    )
  }

  const token = await login(apiBase, email, password)
  process.env.CALCTREE_BEARER = token
  return token
}
