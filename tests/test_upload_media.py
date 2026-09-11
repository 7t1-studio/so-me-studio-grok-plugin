"""Offline behavioral tests: no real files or signed URLs leave the test process."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "upload_media.py"
SPEC = importlib.util.spec_from_file_location("upload_media", SCRIPT)
upload_media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(upload_media)


class FakeConnection:
    def __init__(self, status=200):
        self.status = status
        self.requests = []
        self.closed = False

    def request(self, method, target, body, headers):
        # Production must pass a stream, not load the full media into memory.
        if not hasattr(body, "read"):
            raise AssertionError("Upload body must be a stream")
        self.requests.append((method, target, body.read(), headers))

    def getresponse(self):
        return type("Response", (), {"status": self.status})()

    def close(self):
        self.closed = True


class UploadTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.payload = b"\x00binary-image\xff\r\n" * 100
        self.media = self.root / "private image.png"
        self.media.write_bytes(self.payload)
        self.item = {
            "fileId": "file-one", "filePath": str(self.media),
            "size": len(self.payload), "mimetype": "image/png",
            "uploadUrl": "https://upload.example.test/media?signature=private-test-signature",
        }

    def test_streams_exact_bytes_and_presign_headers(self):
        connection = FakeConnection(204)
        output = io.StringIO()
        with patch.object(upload_media.http.client, "HTTPSConnection", return_value=connection) as factory:
            with redirect_stdout(output):
                results = upload_media.upload([self.item])
        factory.assert_called_once_with("upload.example.test", 443, timeout=300)
        self.assertEqual(connection.requests, [("PUT", "/media?signature=private-test-signature",
                         self.payload, {"Content-Type": "image/png", "Content-Length": str(len(self.payload))})])
        self.assertEqual(results, [{"fileId": "file-one", "uploaded": True, "verificationRequired": True}])
        self.assertEqual(json.loads(output.getvalue()), results[0])
        self.assertTrue(connection.closed)

    def test_validates_every_file_before_any_network(self):
        invalid = dict(self.item, fileId="file-two", size=len(self.payload) + 1)
        with patch.object(upload_media.http.client, "HTTPSConnection") as factory:
            with self.assertRaises(ValueError):
                upload_media.upload([self.item, invalid])
        factory.assert_not_called()

    def test_rejects_mismatched_size_mime_and_unsafe_urls(self):
        changes = [
            {"size": 0}, {"size": True}, {"size": str(len(self.payload))},
            {"size": len(self.payload) - 1}, {"mimetype": "application/json"},
            {"mimetype": "image/png\r\nAuthorization: leaked"},
            {"uploadUrl": "http://upload.example.test/media"},
            {"uploadUrl": "https://user:password@upload.example.test/media"},
            {"uploadUrl": "https://upload.example.test/media#fragment"},
        ]
        for change in changes:
            with self.subTest(change=change):
                with patch.object(upload_media.http.client, "HTTPSConnection") as factory:
                    with self.assertRaises(ValueError):
                        upload_media.upload([dict(self.item, **change)])
                factory.assert_not_called()

    def test_missing_file_does_not_start_network(self):
        with patch.object(upload_media.http.client, "HTTPSConnection") as factory:
            with self.assertRaises(FileNotFoundError):
                upload_media.upload([self.item, dict(self.item, filePath=str(self.root / "missing.png"))])
        factory.assert_not_called()

    def test_redirect_is_a_failure_and_never_retried(self):
        connection = FakeConnection(307)
        output = io.StringIO()
        with patch.object(upload_media.http.client, "HTTPSConnection", return_value=connection) as factory:
            with redirect_stdout(output), self.assertRaisesRegex(RuntimeError, "HTTP 307"):
                upload_media.upload([self.item])
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(len(connection.requests), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertTrue(connection.closed)

    def test_partial_success_is_reported_once_then_stops(self):
        first, second = FakeConnection(200), FakeConnection(503)
        plan = [dict(self.item, fileId=f"file-{index}") for index in range(1, 4)]
        output = io.StringIO()
        with patch.object(upload_media.http.client, "HTTPSConnection", side_effect=[first, second]) as factory:
            with redirect_stdout(output), self.assertRaises(RuntimeError):
                upload_media.upload(plan)
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(len(first.requests), 1)
        self.assertEqual(len(second.requests), 1)
        self.assertEqual([json.loads(line) for line in output.getvalue().splitlines()],
                         [{"fileId": "file-1", "uploaded": True, "verificationRequired": True}])
        self.assertTrue(first.closed and second.closed)

    def test_cli_redacts_exception_urls_and_local_paths(self):
        plan_path = self.root / "private-plan.json"
        plan_path.write_text(json.dumps([self.item]), encoding="utf-8-sig")
        private_error = f"failed {self.item['uploadUrl']} while reading {self.media}"
        errors, output = io.StringIO(), io.StringIO()
        with patch("sys.argv", [str(SCRIPT), str(plan_path)]):
            with patch("http.client.HTTPSConnection", side_effect=OSError(private_error)):
                with redirect_stderr(errors), redirect_stdout(output), self.assertRaises(SystemExit) as stopped:
                    runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn("OSError", errors.getvalue())
        self.assertIn("verify completed file IDs before retrying", errors.getvalue())
        for secret in (self.item["uploadUrl"], str(self.media), str(plan_path), "private-test-signature"):
            self.assertNotIn(secret, errors.getvalue() + output.getvalue())

    def test_plan_limits_are_checked_offline(self):
        with patch.object(upload_media.http.client, "HTTPSConnection") as factory:
            for plan in (None, {}, [], [self.item] * 21):
                with self.subTest(length=len(plan) if plan is not None else None):
                    with self.assertRaises(ValueError):
                        upload_media.upload(plan)
        factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
