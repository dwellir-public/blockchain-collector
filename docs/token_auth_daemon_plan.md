# Token-Based Auth for Daemon — Implementation Plan

## Goal
Add an opt-in token-based authentication layer to the daemon HTTP endpoints so that requests without the correct token are rejected. Support multiple tokens with add/remove (revocation) so one token can be revoked while others still work. Auth is disabled by default; no prior implementation to preserve.

## High-Level Approach
- Accept a shared secret token via configuration (env var and config file).
- Require the token on all daemon HTTP endpoints (read/list/health/etc.) when configured.
- Keep current behavior when no token is set.
- Log auth failures without leaking the token; avoid timing side channels where feasible.

## Steps
1) **Config surface**
   - Allow multiple tokens: `DAEMON_AUTH_TOKENS` as a comma-separated env var; config entry `auth_tokens: [..]` (single token allowed as a one-element list/string).
   - Allow file-based token store: `DAEMON_AUTH_TOKEN_FILE` or config `auth_token_file` pointing to a JSON/YAML list of `{token, label}` items (token = secret; label = client/name for logging). File wins over env if provided.
   - Update docs/help strings to describe tokens, defaults, revocation, and file format.

2) **Request parsing**
   - Decide accepted header(s): prefer `Authorization: Bearer <token>`; optionally allow `X-Auth-Token` for simplicity.
   - Add a small helper to extract the presented token and compare against the allowed token set.

3) **Middleware/guard**
   - Introduce an auth guard for the daemon server framework (inspect request before handler).
   - If tokens are configured (env/config/file):
     - Compare presented token against the allowed set (constant-time compare per candidate, short-circuit on first match).
     - On missing/invalid token: respond `401 Unauthorized` with a generic message and `WWW-Authenticate: Bearer` header.
     - When logging failures, include the label/client of the mismatched token only if a matching token entry was found; never log raw tokens.
   - If no tokens are configured: bypass auth (current behavior).

4) **Handler integration**
   - Apply the auth guard to all daemon routes; keep health/ping behind auth as well unless explicitly decided otherwise.
   - Ensure error responses stay JSON (or consistent with existing format).

5) **Logging & metrics**
   - Log auth failures at warning level without including the supplied token.
   - If token entries have labels (from file/config), include the label/client name when a presented token matches an entry but is revoked/disabled, or when tracking failed attempts per label.
   - Optionally add counters for failed auth attempts and token hits/misses if metrics exist.

6) **Tests**
   - Unit/functional tests for:
     - No token configured → requests succeed.
     - Single token configured → requests without/with wrong token get 401; correct token succeeds.
     - Multiple tokens configured → any valid token succeeds; revoked token fails.
     - Token file with labels → correct token succeeds; wrong token logs with no secret leakage; labels surface in failure logs when applicable.
     - Header variants and malformed Authorization headers.
     - Constant-time compare helper behavior.

7) **Docs & examples**
   - Update README/daemon docs with how to enable (`DAEMON_AUTH_TOKEN=... dwellir-harvester daemon ...`).
   - Add a curl example using `Authorization: Bearer`.

## Validation
- Run test suite plus new auth tests.
- Manual curl checks with and without token to confirm 200 vs 401 behavior.

## Backward Compatibility / Rollout
- Default: token unset → no change in behavior.
- When set: all endpoints require token; call out in release notes.
