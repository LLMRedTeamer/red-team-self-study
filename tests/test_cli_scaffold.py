# tests/test_cli_scaffold.py

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cli_scaffold import fetch_and_save
import json
import unittest
from unittest.mock import patch, Mock
import tempfile
import requests

class TestCLIScaffold(unittest.TestCase):
    def setUp(self):
        # temp dir for output files so we don't pollute the repo
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out.json"

    def tearDown(self):
        self.tmp.cleanup()

    @patch("tools.cli_scaffold.requests.get")
    def test_json_endpoint_saves_json(self, mock_get):
        resp = Mock()
        resp.status_code = 200
        resp.headers = {"Content-Type": "application/json"}
        resp.json.return_value = {"hello": "world"}
        resp.text = '{"hello":"world"}'
        mock_get.return_value = resp

        info = fetch_and_save("https://example.com/json", 5.0, self.out, verbose=0)

        self.assertEqual(info["status"], 200)
        self.assertEqual(info["kind"], "json")
        saved = json.loads(Path(info["out"]).read_text(encoding="utf-8"))
        self.assertEqual(saved, {"hello": "world"})

    @patch("tools.cli_scaffold.requests.get")
    def test_nonjson_endpoint_saves_text(self, mock_get):
        resp = Mock()
        resp.status_code = 200
        resp.headers = {"Content-Type": "text/html"}
        resp.text = "<html>ok</html>"
        resp.json.side_effect = ValueError("not json")
        mock_get.return_value = resp

        info = fetch_and_save("https://example.com/html", 5.0, self.out, verbose=0)

        self.assertEqual(info["status"], 200)
        self.assertEqual(info["kind"], "text")
        self.assertIn("ok", Path(info["out"]).read_text(encoding="utf-8"))

    @patch("tools.cli_scaffold.requests.get")
    def test_timeout_raises(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("boom")
        with self.assertRaises(requests.exceptions.Timeout):
            fetch_and_save("https://example.com/slow", 0.001, self.out, verbose=0)

if __name__ == "__main__":
    unittest.main()
