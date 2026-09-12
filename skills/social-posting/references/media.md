# Media validation and upload

## Check all intended destinations first

For existing media, use `list_media`, `search_media`, or `list_media_folders` to select the intended library files. For new uploads, obtain the actual source bytes, filename, MIME type, and exact size in bytes. Measure `durationSeconds` when available; never replace known metadata with a guess.

Call `validate_post_media` with **all requested destinations** before allocating uploads or creating any posts. Always call it when you generated, edited, or picked the media yourself: resolution, aspect ratio, codec, and frame rate are the most common reason a post fails hours later at publish time. Use `get_media_rules` for the per-platform table of accepted types, byte caps, attachment counts, duration, pixel bounds, aspect-ratio ranges, video codecs, and frame-rate caps; read it before generating media so the file is the right size in the first place. Send local `files` metadata or library `fileIds`; the service checks workspace ownership and completed uploads for library files. Before publishing a saved draft, validate its saved media and target again.

Present a compact per-destination comparison: destination/post type, filename, actual size/type, accepted types and size/count/duration limits, and any rejection or unknown check. Use returned limits, which describe So-me Studio's configured rules rather than the platform's definitive current API limits. Sizes use binary MiB (1,048,576 bytes).

- `passes_basic_checks`: declared type, size, and count pass configured checks; publication is not guaranteed.
- `needs_review`: some checks remain unknown, such as duration or uninspected video codecs/dimensions. Do not call unchecked video fully supported.
- `incompatible`: known failure or missing configured rules.

Library files are measured from their own bytes, so the report compares the measured width, height, duration, video codec, and frame rate against each destination's rules. Four issue codes report those properties: `DIMENSIONS_INVALID`, `ASPECT_RATIO_INVALID`, `CODEC_UNSUPPORTED`, and `FRAME_RATE_INVALID`. Each one carries `measured`, `required`, and a `fix` string naming the exact change, for example the crop dimensions for an aspect-ratio failure, plus `suggestedDimensions`. When you produced the media, apply the `fix` (crop or resize), then call `validate_post_media` again and continue only after it passes. When the user supplied the media, show the `fix` and let the user choose. For a file that is not uploaded yet, send the measured `width`, `height`, `durationSeconds`, `videoCodec`, and `frameRate` in `files`; every property you omit becomes a `needs_review` warning instead of a pass. Never guess a measurement.

If **any** destination is incompatible or needs review, show the full comparison and obtain the user's choice **before creating posts on any destination**. Offer applicable choices: selected destinations, another file, conversion/compression/trimming with permission and available capabilities, another post type, saving a draft, or cancellation. Honor an existing decision for these exact files/destinations and disclosed limitations.

A general cross-post request does not authorize dropping destinations or altering files. Do not automatically convert, compress, crop, trim, replace attachments, switch post types, or partially publish. Known size/type/count failures require different media, a supported post type, or a selected compatible destination; accepting a warning cannot override them. Unknown inspection results can be explicitly accepted but must remain described as unchecked. Recheck affected destinations after any file, post-type, or destination change.

Incompatible drafts can be saved for later editing. Failed conversion preserves the draft. Later platform/account failures are still possible: if an authorized multi-destination publish partly succeeds, report each actual result and reason, preserve successes, and let the user choose the next action. Never retry successful destinations automatically.

## Upload actual bytes

1. Ensure the source file exists on the computer executing the upload. Grok Bot normally uses its cloud filesystem, not a Windows/macOS path on the user's laptop. Use an available attachment-download capability to obtain source bytes when supported; an attachment URL is not a local path.
2. After the compatibility decision above, call `presign_media_upload` with `files: [{filename, mimetype, size}]` and optional `folderId`. Each response supplies `fileId`, `uploadUrl`, and `fileSrc` in input order. This only reserves a library entry.
3. PUT raw file bytes to each `uploadUrl` with the same `Content-Type`. Use an available HTTP upload capability or the bundled [Python upload helper](../../../scripts/upload_media.py). The helper requires Python 3 and a source file accessible on the execution computer. Resolve the helper from this installed plugin; do not assume the plugin is in the current working directory.
4. Call `get_media_file` with the returned ID and `verifyUpload: true`. Continue only after backend verification succeeds. A reserved ID or a 2xx PUT does not replace verification. Stop before publishing on upload failure. Reuse a still-valid upload URL for retrying the same bytes rather than allocating duplicate entries.
5. Pass the ordered `fileIds` and matching `postType` to `create_post` or `create_draft` as authorized.

The upload helper accepts a path to a temporary JSON array, with `filePath`, `fileId`, `uploadUrl`, `mimetype`, and exact `size` for each upload. Invoke it as `python3 <plugin-root>/scripts/upload_media.py <private-plan.json>` (or the available Python 3 executable). Keep signed URLs out of user-visible output and remove the temporary plan after use. The helper sends no So-me Studio credentials to storage. Its `uploaded: true` result still requires the backend verification in step 4. If some uploads completed before failure, verify those IDs before retrying.

If the client cannot access the source bytes or perform PUT, have the user upload through So-me Studio's media library and continue with its IDs. Never silently publish without the requested attachment; a caption URL is not an attachment.

## Drafts and attachment replacement

Drafts retain IDs in `metaData.mediaFileIds` and preview URLs in `metaData.mediaUrls`. `convert_draft` uses the saved IDs unless explicit replacement `fileIds` are supplied; the service checks uploaded bytes again before conversion. Posts receive independent media copies. On older drafts with URLs but no IDs, select or upload library files and attach their IDs before converting.

Use `update_post` or `update_draft` with the **complete replacement** `fileIds` list. Omitting `fileIds` preserves attachments; `fileIds: []` clears them. Also set `postType: "TEXT"` when changing a post to text only. Already published posts cannot have media replaced through this tool.

The backend accepts at most 20 files per request, and platform limits can be lower. Dimensions, duration, codecs, and platform-specific options also matter. Never promise every file is valid for every destination.
