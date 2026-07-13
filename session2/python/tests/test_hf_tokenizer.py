"""Legacy hf_bpe smoke tests — superseded by test_faithful_roundtrip.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="legacy hf_bpe pipeline; see test_faithful_roundtrip.py")
