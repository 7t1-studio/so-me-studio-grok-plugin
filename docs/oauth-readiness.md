# OAuth readiness for Cursor and Grok Bot

Checked 11 September 2026. The public production checks in [live-checks.json](live-checks.json) passed. They verify discovery and rejection of unauthenticated account access. They do not establish a successful Cursor or Grok Bot login.

**Follow-up verification:** a live registration request at 10:15 UTC on September 11 returned HTTP 400, `redirect_uri not allowed`, for the exact documented Cursor web callback. No client, secret, or authenticated session was created. This is now a confirmed production blocker rather than an unknown environment setting. See [callback-verification.json](callback-verification.json).

## Connection contract

The plugin uses Streamable HTTP at `https://api.so-me.studio/mcp/posting`. OAuth discovery advertises authorization code flow with PKCE `S256`, refresh tokens, scope `mcp`, dynamic client registration (DCR), and client ID metadata documents (CIMD). The advertised token endpoint authentication methods are `none` and `client_secret_post`. A public PKCE client can use `none` without packaging a secret.

| Item | URL |
| --- | --- |
| Protected resource | `https://api.so-me.studio/mcp/posting` |
| Resource metadata | `https://api.so-me.studio/.well-known/oauth-protected-resource/mcp/posting` |
| Authorization-server metadata | `https://api.so-me.studio/.well-known/oauth-authorization-server` |
| Authorization | `https://api.so-me.studio/oauth/authorize` |
| Token exchange | `https://api.so-me.studio/oauth/token` |
| Dynamic registration | `https://api.so-me.studio/oauth/register` |

## Callback prerequisite

Cursor documents two fixed callbacks: `https://www.cursor.com/agents/mcp/oauth/callback` for web and Cursor Agents, and `http://localhost:8787/callback` for the desktop app. Register the callbacks for the surfaces being tested. [Cursor MCP documentation](https://cursor.com/docs/mcp#static-redirect-url)

The inspected backend source, `apps/backend/src/api/mcp/oauth/mcp-oauth.service.ts`, accepts the desktop URI through its loopback rule. Its default DCR callback allowlist does **not** include the Cursor web URI. The prepared backend fix permits this exact URI during registration:

```text
https://www.cursor.com/agents/mcp/oauth/callback
```

The subsequent live registration test confirms that production currently rejects this URI. The prepared change retains registered-client validation: an unknown client or a client registered with another callback cannot authorize through the Cursor callback. The focused OAuth suite passes 63 tests, including 11 spoofed or modified callback variants. The fix is not deployed yet. Do not put this callback into a static-client shortcut or add guessed variants or broad domain wildcards.

The server also supports CIMD. Successful metadata discovery alone does not show which client-registration flow Grok Bot uses or prove that either flow completes.

## Resource and authentication discovery

The backend binds OAuth tokens to one MCP resource. Authorization must select `resource=https://api.so-me.studio/mcp/posting` and scope `mcp`. In the inspected source, omitting the resource selects the full `/mcp` endpoint; that token is rejected by `/mcp/posting`. Token exchange and refresh cannot switch the selected resource. Reconnect specifically to the posting endpoint when an existing token belongs to another endpoint.

Production currently allows anonymous protocol discovery: `tools/list` returns HTTP 200 with 30 public tool schemas and a `WWW-Authenticate` header. An anonymous `list_accounts` invocation returns an MCP error result with `_meta["mcp/www_authenticate"]` and no account data. Each tool declares the OAuth scope and a compatibility metadata mirror. This behavior was designed for clients that recognize in-chat authentication challenges. Public checks do **not** prove that Grok Bot recognizes this pattern and opens its native authentication flow. If Grok Bot lists tools but never offers authentication, inspect the client's MCP error and supported authentication behavior before changing the server or declaring success.

The posting URL restricts the exposed tool catalog. It does not introduce a narrower OAuth scope. Existing workspace membership, API/MCP entitlement, connected-account state and credits still govern authenticated use.

## Client acceptance before submission

1. Load this repository as a Cursor plugin using the current documented development flow and confirm that it discovers the `so-me-studio` MCP server. For Grok Bot, confirm availability in the intended plugin surface; local Cursor installation does not by itself prove Grok Bot availability.
2. Start the native Authenticate/Connect flow. Verify the actual callback and resource against the values above. Complete sign-in and consent in the service browser UI. Keep passwords, tokens, signed upload URLs and authorization codes out of repository files and review screenshots.
3. Confirm the plugin appears installed and that a read-only `list_accounts` call succeeds in the intended workspace. Verify reconnect behavior after disconnecting the test connection, and test token refresh through the client when practical.
4. Save and read back a clearly identified test draft to verify write behavior. Use an explicitly authorized test destination and content for scheduling, cancellation and publication acceptance. Do not report a queued post as published.
5. Validate Grok Bot's actual attachment access before claiming local upload support. If it can access the bytes and perform HTTPS PUT, reserve an upload, transfer the exact bytes, and verify through `get_media_file` with `verifyUpload: true`. Otherwise test existing media-library file IDs and document that supported route.
6. Record the client version, test date, actual outcomes and any remaining limitations in the submission packet. Public metadata checks and historical tests from another client are not a substitute for this acceptance record.

Grok Bot connects plugins through its Plugins UI and browser authorization. Its connection belongs to the signed-in account. [Grok Bot plugin help](https://cursor.com/help/grok-bot/connect-plugins) Connector OAuth tokens stay on Cursor's backend; the plugin does not need a bundled user token. [Grok Bot security documentation](https://cursor.com/docs/grok-bot/security#identity-and-sign-ins)
