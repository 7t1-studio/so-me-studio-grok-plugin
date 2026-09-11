# Documentation checked on September 11, 2026

Use these primary sources when updating the plugin. Documentation and client rollout can change; recheck before a release.

| Source | What it establishes |
| --- | --- |
| [xAI: Grok Bot settings](https://docs.x.ai/grok-bot/settings-and-notifications) | Marketplace/Yours plugin management; page updated September 2, 2026. |
| [xAI: Computer and apps](https://docs.x.ai/grok-bot/computer-and-apps) | Plugins are connected services; account-wide access; cloud files differ from local files. |
| [Cursor: Connect plugins in Grok Bot](https://cursor.com/help/grok-bot/connect-plugins) | Grok Bot uses Cursor marketplace plugins and account-scoped connections. |
| [Cursor: Plugin reference](https://cursor.com/docs/reference/plugins) | `.cursor-plugin/plugin.json`, root `mcp.json`, skill discovery, relative logo paths, public Git repository submission. |
| [Cursor: Plugin development](https://cursor.com/docs/plugins) | Local imports under `~/.cursor/plugins/local`, reload and component checks. |
| [Cursor: MCP](https://cursor.com/docs/mcp) | Streamable HTTP/OAuth and exact web and desktop callbacks. |
| [Cursor: Publisher application](https://cursor.com/marketplace/publish) | Live application fields and repository submission. |
| [So-me Studio: MCP](https://docs.so-me.studio/mcp/overview) | Product connection context; runtime tool schemas remain authoritative. |

## Distribution scope

Grok Bot plugins are submitted through the Cursor publisher application. The live form is titled “Become a plugin publisher” and requires organization name/handle, contact email, logo URL, description, public repository, and website. Clicking Submit Application also accepts the linked Publisher Terms. Preparation of this repository does not submit that form or accept those terms.

Other Grok surfaces have distinct distribution mechanisms. [Grok Build's marketplace](https://github.com/xai-org/plugin-marketplace) is a GitHub catalog with commit-pinned plugin sources and pull request review. [Grok chat connectors](https://docs.x.ai/grok/connectors) can use custom MCP URLs. This release targets Grok Bot and does not claim a Build listing, a built-in grok.com connector, or a shared Bot-template listing.
