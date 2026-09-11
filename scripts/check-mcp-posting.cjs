// Credential-free deployment smoke test. Never creates a post or OAuth session.
const assert = require('node:assert/strict');
const expectedTools = [
  'validate_post_media', 'list_posts', 'get_post', 'create_post', 'update_post',
  'schedule_post', 'unschedule_post', 'delete_post', 'retry_post', 'get_calendar_posts',
  'list_drafts', 'get_draft', 'create_draft', 'update_draft', 'delete_draft', 'convert_draft',
  'list_accounts', 'get_account', 'list_media', 'search_media', 'get_media_file',
  'list_media_folders', 'presign_media_upload', 'list_pinterest_boards',
  'list_reddit_subreddits', 'list_reddit_flairs', 'list_gmb_locations',
  'list_discord_channels', 'list_slack_channels', 'get_tiktok_creator_info',
];

async function checkMcpPosting(baseUrl = 'https://api.so-me.studio', fetchImpl = fetch) {
  const origin = new URL(baseUrl).origin;
  assert.equal(new URL(origin).protocol, 'https:', 'Use an HTTPS service origin');
  async function request(path, status, options = {}) {
    const response = await fetchImpl(`${origin}${path}`, {
      ...options, redirect: 'manual', signal: AbortSignal.timeout(15000),
    });
    assert.equal(response.status, status, `${path} returned ${response.status}, expected ${status}`);
    return response;
  }
  const health = await (await request('/health', 200)).json();
  assert.equal(health.status, 'ok', 'Backend health is not ok');
  const metadataPath = '/.well-known/oauth-protected-resource/mcp/posting';
  const metadata = await (await request(metadataPath, 200)).json();
  assert.equal(metadata.resource, `${origin}/mcp/posting`, 'Posting resource mismatch');
  assert.deepEqual(metadata.authorization_servers, [origin], 'OAuth issuer mismatch');
  const oauth = await (await request('/.well-known/oauth-authorization-server', 200)).json();
  assert.equal(oauth.issuer, origin, 'Authorization issuer mismatch');
  assert.ok(oauth.code_challenge_methods_supported?.includes('S256'), 'PKCE S256 missing');
  for (const key of ['authorization_endpoint', 'token_endpoint', 'registration_endpoint'])
    assert.equal(new URL(oauth[key]).origin, origin, `${key} points to a different origin`);
  async function rpc(method, params = {}) {
    const response = await request('/mcp/posting', 200, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
    });
    const text = await response.text();
    return JSON.parse(response.headers.get('content-type')?.includes('text/event-stream')
      ? text.split('\n').find((line) => line.startsWith('data: ')).slice(6) : text);
  }
  const listed = await rpc('tools/list');
  assert.deepEqual(listed.result?.tools?.map(tool => tool.name).sort(), [...expectedTools].sort(),
    'Posting tool catalog missing or changed unexpectedly');
  for (const tool of listed.result.tools) {
    assert.deepEqual(tool.securitySchemes, [{ type: 'oauth2', scopes: ['mcp'] }], `${tool.name} OAuth policy missing`);
    assert.deepEqual(tool._meta?.securitySchemes, tool.securitySchemes, `${tool.name} OAuth metadata missing`);
  }
  // Read-only call: even a broken guard must never publish during a smoke test.
  const denied = await rpc('tools/call', { name: 'list_accounts', arguments: {} });
  assert.equal(denied.result?.isError, true, 'Anonymous account access was not denied');
  const challenges = denied.result?._meta?.['mcp/www_authenticate'];
  assert.ok(challenges?.some((value) => value.includes(`resource_metadata="${origin}${metadataPath}"`) && value.includes('error="invalid_token"') && value.includes('error_description=')), 'Posting in-chat OAuth challenge missing');
  assert.equal(denied.result?.structuredContent, undefined, 'Anonymous response contains account data');
  for (const method of ['GET', 'DELETE']) {
    const response = await request('/mcp/posting', 405, { method });
    await response.arrayBuffer();
  }
  return {
    checkedAtUtc: new Date().toISOString(), endpoint: `${origin}/mcp/posting`,
    health: 'ok', postingMetadata: 'ok', oauthDiscovery: 'ok',
    expectedToolCount: expectedTools.length, authenticationRequired: true,
    statelessTransport: 'ok', authenticatedClientVerified: false,
  };
}

module.exports = { checkMcpPosting };
if (require.main === module) {
  checkMcpPosting(process.argv[2]).then(result => console.log(JSON.stringify(result, null, 2)))
    .catch(error => {
      console.error(`Public MCP check failed: ${error.message}`);
      process.exitCode = 1;
    });
}
