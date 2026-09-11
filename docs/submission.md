# Publisher submission preparation

Prepared September 11, 2026. Target: **Grok Bot through the Cursor Marketplace**. Application: https://cursor.com/marketplace/publish

## Application copy

| Field | Prepared value |
| --- | --- |
| Organization name | 7t1 Studio |
| Organization handle | 7t1-studio |
| Contact email | support@so-me.studio |
| GitHub repository | https://github.com/7t1-studio/so-me-studio-grok-plugin |
| Website URL | https://so-me.studio |
| Description | Social media studio connects Grok Bot to So-me Studio for drafting, publishing, and scheduling social posts. Includes connected-account lookup, image/video upload workflows, media compatibility checks, saved drafts, and calendar management through a hosted OAuth MCP service. Requires a So-me Studio workspace with API/MCP access and connected social accounts. |

Use the commit-pinned raw URL of `assets/icon.png` from the release commit for the Logotype URL. The public icon must remain reachable. Organization-handle availability is decided by the submission service.

## Reviewer connection and demo

1. Load the plugin and verify that the social-posting skill and `so-me-studio` MCP server are discovered.
2. Complete browser OAuth for a workspace with MCP access. Confirm callback registration and the exact posting `resource` per [OAuth readiness](oauth-readiness.md).
3. Ask “Show my connected social accounts.” Confirm actual workspace account data appears without exposing credentials.
4. Ask for upcoming posts and drafts. Confirm the correct workspace and pagination.
5. In a dedicated test workspace, explicitly request a draft with a small test image. Confirm media preflight, upload, backend verification, and saved draft attachments.
6. Request scheduling only to a controlled test social account, using an explicit future timestamp and timezone. Confirm the queue result and retrieve the stored post. Cancel that test schedule when explicitly requested.
7. Test incompatible media and an ambiguous request to write copy. The plugin should explain the incompatibility or prepare copy without silently publishing.

No reviewer credentials are included in this public repository. Provision a review workspace through an approved private channel if reviewers require it.

## Current evidence and remaining checks

- Local verification on September 11, 2026: package validation passed; all 18 offline unit tests passed on Windows/Python 3.12; the skill frontmatter validator passed.
- A repeat public probe on September 11, 2026 at 09:59 UTC passed health, discovery, the exact 30-tool catalog, and anonymous account-access rejection.
- CI is configured for Ubuntu/Python 3.12 and Windows/Python 3.13. Its run status is visible in the repository Actions tab.
- Public production discovery and unauthenticated access behavior are recorded in [live-checks.json](live-checks.json).
- Authenticated Grok Bot login and posting have **not** been verified by those checks.
- The production Cursor web OAuth callback allowlist must be confirmed; source code alone cannot establish the deployed environment value.
- Publisher application submission and marketplace approval are pending.

Do not claim that anonymous tool discovery proves an authenticated installation works. Keep the pending items visible to the reviewer and complete the controlled acceptance run before representing this release as fully tested in Grok Bot.

## Final submission

Review the prefilled application in the signed-in browser, confirm the publishing identity, and review the linked Publisher Terms. Click **Submit Application** only when the pending integration checks are resolved and the publisher is ready to accept the terms. Retain the resulting application status or confirmation; an open form is not a submitted application.
