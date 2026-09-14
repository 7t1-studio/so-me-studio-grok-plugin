# Social media studio for Grok Bot

Draft, publish, and schedule social posts from Grok Bot using your connected So-me Studio accounts. Includes image/video upload guidance, saved drafts, media compatibility checks, calendar lookup, and management of upcoming posts.

This is a **Cursor-format plugin for Grok Bot**, maintained by 7t1 Studio. Grok Bot uses Cursor marketplace plugins ([connection guide](https://cursor.com/help/grok-bot/connect-plugins)). The package connects directly to So-me Studio's hosted MCP service; it does not run a new backend or require an xAI API key.

**Release status:** version 1.1.0 adds thread chains, the automatic first comment, typed TikTok options, measured media checks, and the required `X-MCP-Auth-Mode: oauth` header. It is prepared for publisher review. Marketplace approval and an authenticated Grok Bot acceptance run are still pending. See [submission preparation](docs/submission.md), [OAuth readiness](docs/oauth-readiness.md), and [public endpoint evidence](docs/live-checks.json).

## What it includes

- Find connected accounts and platform-specific posting destinations.
- Save/edit drafts and attach existing library media or uploaded images/videos.
- Compare media compatibility across every requested destination before publication, including pixel size, aspect ratio, codec, and frame rate.
- Publish a multi-post chain on X, Threads, Bluesky, or Mastodon with `threadParts`.
- Add an automatic first comment for hashtags or a link on the platforms that support one.
- Collect the TikTok privacy level and interaction options from the creator before publication.
- Publish now, schedule with a timezone, reschedule, or cancel upcoming posts.
- Review the calendar and report actual publication status.

The posting endpoint exposes 31 tools. Analytics, inbox messaging, account administration, bulk deletion, and AI image/video generation are outside this plugin. Supported formats and post types depend on the destination and workspace entitlements. Telegram and WhatsApp are outside the scheduler posting flow.

## Connect

Once approved, find **Social media studio** in Grok Bot's Plugins marketplace, add it, and complete the So-me Studio browser authorization. Installed plugins are available across the Bots on the same account. Attach the plugin in a task when needed.

You need a So-me Studio workspace with API/MCP access, sufficient credits, and the intended social accounts already connected. Entitlements shown in your workspace are authoritative.

| Setting | Value |
| --- | --- |
| Transport | Streamable HTTP |
| MCP URL | `https://api.so-me.studio/mcp/posting` |
| Authentication | Browser OAuth with PKCE |
| Non-secret connection header | `X-MCP-Auth-Mode: oauth` |
| Scope | `mcp` |
| Request header | `X-MCP-Auth-Mode: oauth` (not a secret) |
| Secrets included in package | None |

The `X-MCP-Auth-Mode: oauth` header in `mcp.json` is **required**. The posting endpoint returns an HTTP 401 OAuth challenge only to a client that sends this header, and Grok Bot needs that challenge to open its native OAuth prompt. Without the header Grok Bot fails the connection with `no_auth_link`. The header carries no credential, so the package still contains no secret. Cursor's MCP configuration supports a `headers` object for a remote server; the package validator accepts this one header and rejects every other header.

The manifest and MCP configuration follow [Cursor's plugin reference](https://cursor.com/docs/reference/plugins). A manifest alone does not register an OAuth client. Maintainers must verify the [documented callback and resource requirements](docs/oauth-readiness.md) before marking the integration production-ready.

## Try it

- “Show my connected social accounts and posts scheduled this week.”
- “Save this caption and attached image as a draft for my Facebook page.”
- “Compare this video's compatibility with my Instagram and Facebook accounts.”
- “Post this X thread: the hook, then three follow-up posts.”
- “Publish this to Instagram and put the hashtags in the first comment.”
- “Schedule this approved draft for September 20, 2026 at 10 AM Asia/Dhaka.”

Writing a caption does not authorize publication. The skill preserves the user's specified content, destinations, and scheduling intent. It treats successful creation as queued until the service confirms publication, and checks ambiguous write failures before retrying.

## Images and videos

For a new file, the workflow validates all target destinations, obtains a signed upload URL, uploads the actual bytes, verifies the stored file, and attaches its ID to a draft or post. A signed URL by itself is not an upload.

Grok Bot's cloud computer is separate from your laptop. A local path on your device is usable only after the file is available to the Bot. You can instead upload media in the [So-me Studio app](https://app.so-me.studio) and select it from the media library.

The optional [Python upload helper](scripts/upload_media.py) needs Python 3.10+ and no third-party dependencies. Run it only with a temporary private upload plan returned by the service:

```sh
python3 scripts/upload_media.py /path/to/private-upload-plan.json
```

The plan is an array of objects containing `filePath`, `fileId`, `uploadUrl`, `mimetype`, and exact `size` in bytes. Do not commit plans or paste signed URLs into chats. The helper sends only the requested file bytes and content headers, does not follow redirects, and reports file IDs requiring backend verification. See the [posting skill](skills/social-posting/SKILL.md) for the complete sequence.

## Develop and validate

```sh
git clone https://github.com/7t1-studio/so-me-studio-grok-plugin.git
cd so-me-studio-grok-plugin
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```

These checks validate package structure and the upload helper without credentials or real uploads. They do not prove a successful OAuth login or a completed social publication.

With Node.js 18+ you can also rerun the public production probe:

```sh
node scripts/check-mcp-posting.cjs
```

It checks health, OAuth metadata, the exact 31-tool catalog, and denial of anonymous account access. It never registers an OAuth client, sends credentials, uploads media, or creates a post.

For a Cursor local import, copy this repository's plugin files into `~/.cursor/plugins/local/so-me-studio`, reload Cursor, and check its components in Customize. Local imports must be allowed by your team's settings. See [official local testing instructions](https://cursor.com/docs/plugins#test-plugins-locally). Local import is not marketplace publication or proof of Grok Bot cloud installation.

## Package contents

```text
.cursor-plugin/plugin.json    Listing metadata and component paths
mcp.json                      Hosted posting MCP configuration
skills/social-posting/        Posting workflow and media guidance
scripts/upload_media.py       Optional streaming upload helper
assets/icon.png               So-me Studio logo
docs/                         Sources, review notes, and verification evidence
tests/                        Offline behavioral checks
```

MIT licensed. The logo, license, and original posting workflow come from [So-me Studio's existing connector](https://github.com/7t1-studio/so-me-studio-chatgpt-plugin). This package is a third-party integration and does not imply endorsement by xAI or Cursor.

[Product](https://so-me.studio) · [MCP documentation](https://docs.so-me.studio/mcp/overview) · [Privacy policy](https://so-me.studio/privacy-policy) · Support: support@so-me.studio
