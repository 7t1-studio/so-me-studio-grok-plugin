#!/usr/bin/env python3
"""PUT local image/video bytes to presigned URLs from a temporary JSON plan."""
import argparse
import http.client
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit


def upload(plan):
    if not isinstance(plan, list) or not 1 <= len(plan) <= 20:
        raise ValueError('Plan must contain 1 to 20 uploads')
    prepared = []
    for item in plan:
        path = Path(item['filePath']).expanduser().resolve(strict=True)
        size = item['size']
        mime = item['mimetype']
        url = urlsplit(item['uploadUrl'])
        if not path.is_file() or type(size) is not int or size <= 0 or path.stat().st_size != size:
            raise ValueError('Local file size must match the presign request')
        if not isinstance(mime, str) or not mime.startswith(('image/', 'video/')) or '\r' in mime or '\n' in mime:
            raise ValueError('Expected an image or video MIME type')
        if url.scheme != 'https' or not url.hostname or url.username or url.password or url.fragment:
            raise ValueError('Expected an HTTPS presigned upload URL without credentials or fragment')
        prepared.append((item['fileId'], path, size, mime, url))
    results = []
    for file_id, path, size, mime, url in prepared:
        connection = http.client.HTTPSConnection(url.hostname, url.port or 443, timeout=300)
        try:
            target = url.path or '/'
            if url.query:
                target += '?' + url.query
            with path.open('rb') as stream:
                connection.request('PUT', target, body=stream, headers={
                    'Content-Type': mime, 'Content-Length': str(size),
                })
                response = connection.getresponse()
                if not 200 <= response.status < 300:
                    raise RuntimeError(f'Upload failed with HTTP {response.status}; no redirect was followed')
            result = {'fileId': file_id, 'uploaded': True, 'verificationRequired': True}
            results.append(result)
            print(json.dumps(result), flush=True)
        finally:
            connection.close()
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', help='Temporary JSON upload plan; contains signed URLs, keep private')
    args = parser.parse_args()
    try:
        upload(json.loads(Path(args.plan).read_text(encoding='utf-8-sig')))
    except Exception as error:
        # Do not print exception messages that may include signed URLs or local paths.
        print(f'Upload stopped ({type(error).__name__}). Check file sizes and URL expiry; verify completed file IDs before retrying.', file=sys.stderr)
        sys.exit(1)
