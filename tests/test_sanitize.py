"""Tests for input sanitization and safe rendering.

Run from the repo root:
    pip install -r requirements-dev.txt
    pytest
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from sanitize import clean_text
from main import app

client = TestClient(app)


def test_strips_control_characters():
    assert clean_text("a\x00b\x07c") == "abc"


def test_keeps_normal_whitespace_then_trims():
    assert clean_text("  hello\nworld  ") == "hello\nworld"


def test_truncates_to_max_len():
    assert len(clean_text("x" * 50, max_len=10)) == 10


def test_handles_none_and_non_str():
    assert clean_text(None) == ""
    assert clean_text(12345) == "12345"


def test_script_payload_is_neutralized_in_response():
    """A <script> payload must come back escaped (shown as text), never raw."""
    payload = "<script>alert('xss')</script>"
    resp = client.post("/", data={"text": payload})
    assert resp.status_code == 200
    body = resp.text
    # The dangerous raw tag must NOT appear...
    assert "<script>alert('xss')</script>" not in body
    # ...it must appear HTML-escaped instead.
    assert "&lt;script&gt;" in body
