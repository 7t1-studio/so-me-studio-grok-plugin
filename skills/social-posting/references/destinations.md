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

## TikTok

Never guess the TikTok privacy level. TikTok rejects every post that carries none, and only the creator may choose one.

1. Call `get_tiktok_creator_info` for the target account.
2. Show the user only the values it returns in `privacy_level_options`. A private account cannot choose `PUBLIC_TO_EVERYONE`.
3. Recommend `PUBLIC_TO_EVERYONE`.
4. Ask whether comments are allowed. Duet and stitch stay on unless the user says otherwise.
5. Pass the answers in the typed `tiktok` object: `{ privacyLevel, allowComments, allowDuet, allowStitch }`.

`create_post`, `update_post`, `schedule_post`, `create_draft`, `update_draft`, and `convert_draft` all take the object. A TikTok post without `tiktok.privacyLevel` is rejected with `TIKTOK_PRIVACY_LEVEL_REQUIRED`; that payload lists the allowed options in `privacyLevelOptions`, so use them instead of guessing. A level the creator cannot use returns `TIKTOK_PRIVACY_LEVEL_NOT_ALLOWED` with the allowed values. A creator who turned comments, duet, or stitch off for the whole account forces the matching option off, and the result carries a `TIKTOK_SETTING_FORCED` warning; repeat each forced change to the user. Set `brandContentToggle` or `brandOrganicToggle` only when the user asks. Any non-TikTok destination rejects the `tiktok` field. A draft may hold the options unvalidated; `convert_draft` validates them and accepts a `tiktok` object of its own. Honor an existing choice for this exact publication; do not broaden visibility.

A connected account may support inbox operations only. Telegram and WhatsApp are outside the scheduler's posting flow. Explain unsupported destinations instead of promising that every connected account can publish.
