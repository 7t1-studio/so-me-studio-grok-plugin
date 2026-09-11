# Destination options

Discover current schemas before using platform-specific `metaData`. Use the read-only destination tools and returned identifiers; do not invent destination IDs or privacy options.

| Destination | Read first | Posting option |
| --- | --- | --- |
| Pinterest | `list_pinterest_boards` | Selected `boardId` |
| Discord | `list_discord_channels` | Selected `discordChannelIds` |
| Slack | `list_slack_channels` | Selected `slackChannelIds` |
| Reddit | `list_reddit_subreddits`, `list_reddit_flairs` | Selected subreddit/flair fields from the live schema |
| Google Business | `list_gmb_locations` | Selected location field from the live schema |

Preserve the user's selection. Ask when several possible destinations remain ambiguous. This plugin selects existing destinations; it does not create boards or manage accounts.

For TikTok, call `get_tiktok_creator_info` before publication. Explain the returned privacy choices and relevant creator limits. Obtain the user's privacy selection and pass `privacy_level`, plus any requested comment/duet/stitch options, in `metaData`. Honor an existing choice for this exact publication; do not guess or broaden visibility.

A connected account may support inbox operations only. Telegram and WhatsApp are outside the scheduler's posting flow. Explain unsupported destinations instead of promising that every connected account can publish.
