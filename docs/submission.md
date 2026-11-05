# Marketplace submission preparation

Refreshed November 5, 2026, for version 1.2.0. Target: the **Grok Bot marketplace**, which xAI shares with Cursor. Form: https://x.ai/bot/marketplace/submit-a-plugin. Submitting accepts Cursor's [Marketplace Publisher Terms](https://cursor.com/marketplace-publisher-terms). Every submission is reviewed before it is listed; xAI has not published review criteria or timelines.

This replaces the September plan to apply through cursor.com/marketplace/publish.

## Form answers

| Field | Prepared value |
| --- | --- |
| First name, last name | The publisher contact's name |
| Work email | support@so-me.studio |
| Organization name | 7t1 Studio |
| Organization handle | `7t1-studio` (lowercase, no spaces; it is the public publisher ID) |
| Website URL | https://so-me.studio |
| Logotype URL | `https://raw.githubusercontent.com/7t1-studio/so-me-studio-grok-plugin/<release-commit>/assets/logo-square.png` |
| Where to list | Grok Bot and Cursor. Leave Grok (coming soon) off until it can be tested. |
| MCP server URL or public GitHub repository | https://github.com/7t1-studio/so-me-studio-grok-plugin |
| Brief description | See below |
| Testing instructions | See below |
| "I've tested this plugin locally and in-app" | Tick only after the [in-app acceptance run](#in-app-acceptance-run) passes |

Submit the **GitHub repository**, not the bare MCP URL. The repository carries the skill and the `X-MCP-Auth-Mode: oauth` header that Grok Bot needs to open its sign-in; a bare URL would connect without that header and fail with `no_auth_link`.

`assets/logo-square.png` is the Social media studio logo on a full-bleed square black plate (1024×1024, no transparency), made from `assets/icon.png` for the form's "1:1 with a background plate" rule. Use the raw URL pinned to the release commit so the logo cannot change after review.

### Brief description

> Plan, schedule, and publish your brand's social media posts from Grok Bot to the accounts connected in Social media studio: X, Facebook, Instagram, LinkedIn, TikTok, YouTube, Threads, Pinterest, Bluesky, Mastodon, and more. Save drafts, write threads, add automatic first comments, check images and videos against each platform's rules, upload media, and manage your posting calendar. Requires a Social media studio account with API/MCP access.

### Testing instructions

Paste this and replace the bracketed line with the review login. The login is kept out of this public repository.

> Social media studio posts to real social accounts, so please use this review workspace.
>
> Connect: add Social media studio, select Authorize on the connect card, and sign in to Social media studio with: [review login and password]. Select "Sign in & allow access". No email code or MFA is needed. The workspace has connected test accounts: X (@hisomestudio), Bluesky (hisomestudio.bsky.social), Mastodon (@somestudio), a Facebook page, and a LinkedIn page (so-me-0047).
>
> 1. "Show my connected social accounts and what's scheduled next week." Read-only: lists the accounts above and the calendar.
> 2. "Write a three-post X thread with tips for batching a week of social posts. Add 'Plan your week with Social media studio' as the first comment and save it as a draft. Don't publish it." One draft for @hisomestudio with two thread parts and the first comment. Nothing is published.
> 3. "Before I upload it, check if my video spring-launch.mp4 (MP4, 1080x1920, 2 minutes, 120 MB, H.264, 30 fps) can go to Instagram Reels, TikTok, Facebook Reels and Bluesky." Read-only: Instagram and TikTok pass; Facebook Reels fails (over 90 seconds) and Bluesky fails (over 100 MiB), each with the fix.
> 4. "Schedule 'New on our blog: 5 ways to plan a week of social posts in 30 minutes.' on my Mastodon account for next Monday at 9:00 AM UTC. Then take it off the schedule." The post is scheduled, then changes to Pending. Nothing is published.
> 5. "Give me a link to upload an image from my computer, then save it as a Facebook draft with the caption 'Hello from Grok Bot'." The Bot returns an upload page (no sign-in, valid for one hour). After you upload a JPG or PNG and say done, it saves a Facebook image draft.
>
> Out of scope: analytics, comment and inbox replies, Reddit, and Google Business Profile. The Bot should say so and post nothing.

The review login is the one used for the ChatGPT review (`reviewer-test-credentials.txt` in the private OpenAI submission backup). Reviewers who publish for real should use Facebook, X, or the LinkedIn page; automatic first comments are paused on LinkedIn.

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
- Not submitted. Marketplace approval is pending.

Do not claim that anonymous tool discovery proves an authenticated installation works.
