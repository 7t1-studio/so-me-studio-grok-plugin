# Marketplace submission preparation

Refreshed November 6, 2026, for version 1.2.0. Target: the **Grok Bot marketplace**, which xAI shares with Cursor. Form: https://x.ai/bot/marketplace/submit-a-plugin. Submitting accepts Cursor's [Marketplace Publisher Terms](https://cursor.com/marketplace-publisher-terms). Every submission is reviewed before it is listed; xAI has not published review criteria or timelines.

This replaces the September plan to apply through cursor.com/marketplace/publish.

## Form answers

| Field | Value entered on November 6, 2026 |
| --- | --- |
| First name, last name | The publisher contact's name |
| Work email | info@so-me.studio |
| Organization name | Social Media Studio |
| Organization handle | `social-media-studio` (lowercase, no spaces; it is the public publisher ID) |
| Website URL | https://so-me.studio |
| Logotype URL | https://raw.githubusercontent.com/7t1-studio/so-me-studio-grok-plugin/17080d60f93ea7df18123abcaa6efdaf443c0136/assets/logo-square.png |
| Where to list | Grok (coming soon), Grok Bot, and Cursor |
| MCP server URL or public GitHub repository | https://github.com/7t1-studio/so-me-studio-grok-plugin |
| Brief description | See below (600-character limit) |
| Testing instructions | See below (600-character limit) |
| "I've tested this plugin locally and in-app" | Ticked after the [in-app acceptance run](#in-app-acceptance-run) passed |

Submit the **GitHub repository**, not the bare MCP URL. The repository carries the skill and the `X-MCP-Auth-Mode: oauth` header that Grok Bot needs to open its sign-in; a bare URL would connect without that header and fail with `no_auth_link`.

`assets/logo-square.png` is the Social media studio logo on a full-bleed square black plate (1024×1024, no transparency), made from `assets/icon.png` for the form's "1:1 with a background plate" rule. Use the raw URL pinned to the release commit so the logo cannot change after review.

### Brief description

> Plan, schedule, and publish your brand's social media posts from Grok Bot to the accounts connected in Social media studio: X, Facebook, Instagram, LinkedIn, TikTok, YouTube, Threads, Pinterest, Bluesky, Mastodon, and more. Save drafts, write threads, add automatic first comments, check images and videos against each platform's rules, upload media, and manage your posting calendar. Requires a Social media studio account with API/MCP access.

### Testing instructions

The form limits this field to 600 characters. The text below is about 475 characters plus the login line, which is kept out of this public repository. Reviewers post for real, so the steps name only the popular destinations: Facebook, X, and the LinkedIn page.

> Add Social media studio, click Authorize and sign in with this login (email/password form):
> [review login]
>
> Then ask Grok Bot:
> 1. "Show my connected social accounts."
> 2. "Create a post 'Testing Social media studio in Grok Bot' with the current time, and publish it now to Facebook, X and my LinkedIn page." Expect three live posts with links.
> 3. "Schedule a post on X for tomorrow 9 AM, then unschedule it."
> Please post only to Facebook, X (@hisomestudio) and the LinkedIn page (so-me-0047).

The current time keeps each reviewer's post unique, so X does not reject a repeat as a duplicate. The longer checks used for the November 5 acceptance run (thread draft, media check, upload link, out-of-scope request) are recorded under [Results](#results-november-5-2026).

## In-app acceptance run

How to repeat it, in Grok Bot with a plan that includes it (Premium or higher):

1. On grok.com open **Dashboard → Customizations → Plugins → Add → Custom MCP**. Name `social-media-studio`, transport HTTP, URL `https://api.so-me.studio/mcp/posting`, header `X-MCP-Auth-Mode: oauth`, no OAuth client ID or secret. Select **Add server**. (Asking a Grok Bot chat to add a custom server also works.)
2. Select **Authenticate** and sign in to Social media studio with the account that owns the test workspace. Use the email and password form, not "Continue with current logged in user", unless the browser is already signed in to that account; the consent page connects the workspace selected in the app's sidebar.
3. Run testing instructions 1 to 5 above in Grok Bot and record the results here.

To switch workspaces later, use the server's **Log out** action on the dashboard, then **Authenticate** again. A custom server proves the connection and the tools. It does not load this package's skill; that happens only once the marketplace plugin is installed.

### Results, November 5, 2026

Grok Bot on the web (grok.com, Premium account), custom server as above, connected to the **Social media studio** workspace (12 connected accounts).

| Check | Result |
| --- | --- |
| Native OAuth prompt | Pass. With the header, the server showed "Needs authentication" and an Authenticate button. |
| Client registration and callback | Pass. Grok registered a public client by DCR and used `redirect_uri=https://www.cursor.com/agents/mcp/oauth/callback`, `resource=https://api.so-me.studio/mcp/posting`, scope `mcp`, PKCE S256. The `/bot/` callback was not used. |
| 1. Accounts and next week's calendar | Pass. Listed all 12 accounts (X @hisomestudio, Bluesky, Mastodon, LinkedIn page so-me-0047, Facebook, Instagram, Threads, TikTok, YouTube, Pinterest, Dribbble, Dev.to) and reported nothing scheduled for next week. |
| 2. X thread draft with first comment | Pass. Saved one draft for @hisomestudio with three posts and the first comment. Nothing published. |
| 3. Video check for four destinations | Pass. Instagram Reels and TikTok pass; Facebook Reels fails on the 90-second limit and Bluesky on the 100 MiB cap, each with a fix. |
| 4. Schedule, then unschedule on Mastodon | Pass. Scheduled for Mon Nov 9 09:00 UTC, unscheduled two seconds later; status Pending. |
| 5. Upload link, then Facebook image draft | Pass. `request_media_upload` returned an upload page; logo-square.png was uploaded through it, and a Facebook image draft was saved with the caption. Nothing published. |
| Out of scope (Reddit, Google Business Profile) | Pass. Declined; nothing posted. |

Issues seen during the run:

- The first two sign-ins did not finish. The app's consent page waited about 11 seconds for `/oauth/consent/details`, showed placeholders, and kept **Allow access** disabled; a reload fixed it. A slow consent page can make a Grok user give up.
- "Continue with current logged in user" connected whichever workspace the app sidebar had selected (first FlowAppz). The consent page names the workspace only as "the workspace selected in the sidebar".
- The upload page always shows a "Using Claude?" tip, also when the link came from Grok Bot.

Test records left in the Social media studio workspace: the X thread draft "Batching a week of social posts (thread)", the Facebook image draft "Hello from Grok Bot", the Pending Mastodon post "New on our blog: 5 ways to plan a week of social posts in 30 minutes.", and logo-square.png in the media library.

## Current evidence

- November 5, 2026: package validation and all 20 offline unit tests pass (Python 3.14 in WSL). The public probe passes against production with the 30-tool catalog, OAuth discovery, the native HTTP 401 challenge with `X-MCP-Auth-Mode: oauth`, and denial of anonymous account access. See [live-checks.json](live-checks.json).
- November 5, 2026: the in-app acceptance run above passed in Grok Bot.
- Submitted through the x.ai form on November 6, 2026, listed for Grok, Grok Bot and Cursor. The form confirmed: "Thanks for submitting your plugin! We'll review it and follow up by email." Marketplace approval is pending; xAI replies to info@so-me.studio.

Do not claim that anonymous tool discovery proves an authenticated installation works.
