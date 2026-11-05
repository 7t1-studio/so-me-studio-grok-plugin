# Social media studio for Grok Bot

Plan, schedule, and publish your brand's social media posts from Grok Bot to the accounts you have connected in Social media studio. Destinations include X, Facebook, Instagram, LinkedIn, TikTok, YouTube, Threads, Pinterest, Bluesky, Mastodon, WordPress, Dev.to, Dribbble, Discord, and Slack. Write and save drafts, schedule a week of posts, create threads, add an automatic first comment, check images and videos against platform rules, and review or change your posting calendar.

This is a **Cursor-format plugin for Grok Bot**, maintained by 7t1 Studio. Grok Bot installs plugins from the marketplace that xAI shares with Cursor. The package connects to Social media studio's hosted MCP service; it does not run a new backend or need an xAI API key.

**Release status:** version 1.2.0 brings the skill in line with the Social media studio plugins for Claude and ChatGPT: the current 30-tool posting catalog, upload links for files that are on the user's device, and Reddit and Google Business Profile marked as unsupported. It is prepared for the [Grok Bot marketplace submission](https://x.ai/bot/marketplace/submit-a-plugin). See [submission preparation](docs/submission.md), [OAuth readiness](docs/oauth-readiness.md), and [public endpoint evidence](docs/live-checks.json).

## What it includes

- Find connected accounts and platform-specific destinations (Pinterest boards, Discord and Slack channels).
- Save and edit drafts, and attach library media or newly uploaded images and videos.
- Check media compatibility across every requested destination before publication, including pixel size, aspect ratio, codec, and frame rate.
- Publish a multi-post chain on X, Threads, Bluesky, or Mastodon with `threadParts`.
- Add an automatic first comment for hashtags or a link on the platforms that support one.
- Collect the TikTok privacy level and interaction options from the creator before publication.
- Publish now, schedule with a timezone, reschedule, or cancel upcoming posts.
- Review the calendar and report actual publication status.

The posting endpoint exposes 30 tools. Analytics, inbox replies, account administration, billing, bulk deletion, and AI image or video generation are outside this plugin. Reddit and Google Business Profile are not supported in this release. Telegram and WhatsApp are outside the posting flow. Supported formats and post types depend on the destination and workspace entitlements.

## Connect

Find **Social media studio** in Grok Bot's plugin marketplace, add it, and sign in to Social media studio in the browser. Installed plugins belong to the Grok Bot account and are available to all of its Bots.

You need a Social media studio workspace with API/MCP access, enough credits, and the social accounts you want to post to already connected. Entitlements shown in your workspace are authoritative.

| Setting | Value |
| --- | --- |
| Transport | Streamable HTTP |
| MCP URL | `https://api.so-me.studio/mcp/posting` |
| Authentication | Browser OAuth with PKCE |
| Request header | `X-MCP-Auth-Mode: oauth` (not a secret) |
| Scope | `mcp` |
| Secrets included in package | None |

The `X-MCP-Auth-Mode: oauth` header in `mcp.json` is **required**. The posting endpoint returns an HTTP 401 OAuth challenge only to a client that sends this header, and Grok Bot needs that challenge to open its sign-in flow. Without the header Grok Bot fails the connection with `no_auth_link`. The header carries no credential, so the package still contains no secret. The package validator accepts this one header and rejects every other header.

The manifest and MCP configuration follow [Cursor's plugin reference](https://cursor.com/docs/reference/plugins). See [OAuth readiness](docs/oauth-readiness.md) for the callback and resource details.

## Try it

- "Show my connected social accounts and the posts scheduled this week."
- "Write a three-post X thread about batching a week of social posts and save it as a draft. Don't publish it."
- "Check whether this 1080x1920, 2-minute, 120 MB video can go to Instagram Reels, TikTok, Facebook Reels, and Bluesky."
- "Give me a link to upload a photo from my phone, then post it to Facebook with the hashtags in the first comment."
- "Schedule this post on Mastodon and my LinkedIn page for next Monday at 9:00 AM UTC, then show next week's calendar."

Writing a caption does not authorize publication. The skill keeps the user's content, destinations, and schedule as given, reports a post as queued until the service confirms publication, and checks ambiguous write failures before retrying.

## Images and videos

Grok Bot works on a cloud computer that is separate from your laptop or phone, so the skill picks an upload route by where the file is:

- **Already in Social media studio:** the Bot finds it in your media library.
- **On your device:** the Bot creates an upload link (`request_media_upload`). Open it, add up to 20 files (no sign-in, valid for one hour), and tell the Bot when you are done.
- **On the Bot's computer** (a file it made or downloaded): the Bot reserves an upload, sends the bytes to the signed URL, and has the service verify the stored file before attaching it.

The optional [Python upload helper](scripts/upload_media.py) handles the last route. It needs Python 3.10+ and no third-party packages. Run it only with a temporary private upload plan returned by the service:

```sh
python3 scripts/upload_media.py /path/to/private-upload-plan.json
```

The plan is an array of objects containing `filePath`, `fileId`, `uploadUrl`, `mimetype`, and exact `size` in bytes. Do not commit plans or paste signed URLs into chats. The helper sends only the file bytes and content headers, does not follow redirects, and reports file IDs that still need backend verification. See the [posting skill](skills/social-posting/SKILL.md) for the complete sequence.

## Develop and validate

```sh
git clone https://github.com/7t1-studio/so-me-studio-grok-plugin.git
cd so-me-studio-grok-plugin
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```

These checks validate the package structure and the upload helper without credentials or real uploads. They do not prove a successful OAuth sign-in or a completed social publication.

With Node.js 18+ you can also rerun the public production probe:

```sh
node scripts/check-mcp-posting.cjs
```

It checks health, OAuth metadata, the exact 30-tool catalog, and denial of anonymous account access. It never registers an OAuth client, sends credentials, uploads media, or creates a post.

To try the server in Grok Bot before the listing is live, ask the Bot in chat: "Add a custom MCP server called social-media-studio at https://api.so-me.studio/mcp/posting with the header X-MCP-Auth-Mode: oauth". Confirm the card, then select **Authorize** on the connect card and sign in to Social media studio. A custom server tests the connection and tools; it does not load this package's skill.

## Package contents

```text
.cursor-plugin/plugin.json    Listing metadata and component paths
mcp.json                      Hosted posting MCP configuration
skills/social-posting/        Posting workflow, media checks, and upload routes
scripts/upload_media.py       Optional streaming upload helper
scripts/check-mcp-posting.cjs Public production probe
assets/icon.png               Social media studio logo
docs/                         Sources, review notes, and verification evidence
tests/                        Offline behavioral checks
```

MIT licensed. The logo, license, and posting workflow are shared with Social media studio's plugins for [ChatGPT](https://github.com/7t1-studio/so-me-studio-chatgpt-plugin) and [Claude](https://github.com/7t1-studio/Social-media-scheduler-claude-connector). This package is a third-party integration and does not imply endorsement by xAI or Cursor.

[Product](https://so-me.studio) · [MCP documentation](https://docs.so-me.studio/mcp/overview) · [Privacy policy](https://so-me.studio/privacy-policy) · [Terms](https://so-me.studio/terms-and-conditions) · Support: support@so-me.studio
