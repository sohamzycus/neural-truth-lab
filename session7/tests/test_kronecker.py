#!/usr/bin/env python3
"""Tests for Session 7 Kronecker research."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "datasets"))

from kronecker.dynamic import DynamicKronecker, dynamic_deterministic_features
from kronecker.fixed import FixedKronecker, fixed_deterministic_features
from kronecker.fourier import FourierKronecker
from decoder.byte_decoder import ByteDecoder
from metrics.reconstruction import find_collisions, reconstruction_report
from kronecker.inverse import deterministic_roundtrip


class TestEncoding(unittest.TestCase):
    def test_ascii_learning_improves(self):
        s = "hello"
        dec = ByteDecoder(latent_dim=64)
        enc = DynamicKronecker()
        latent, _ = enc.encode_deterministic(s)
        raw = s.encode("utf-8")
        before = reconstruction_report(s, dec.decode_string(latent, length=len(raw)))["byte_accuracy"]
        dec.train([(latent, raw)], steps=400)
        after = reconstruction_report(s, dec.decode_string(latent, length=len(raw)))["byte_accuracy"]
        self.assertGreaterEqual(after, before)

    def test_fixed_overflow_flag(self):
        long_s = "a" * 50
        _, meta = fixed_deterministic_features(long_s)
        self.assertTrue(meta["truncated"])
        self.assertGreater(meta["overflow_bytes"], 0)

    def test_dynamic_no_waste_on_short(self):
        _, meta = dynamic_deterministic_features("hi")
        self.assertEqual(meta["waste_bytes"], 0)

    def test_deterministic_same_input(self):
        enc = DynamicKronecker()
        a, _ = enc.encode_deterministic("test")
        b, _ = enc.encode_deterministic("test")
        self.assertEqual(a, b)

    def test_unicode_hindi(self):
        enc = DynamicKronecker()
        latent, meta = enc.encode_deterministic("नमस्ते")
        self.assertGreater(meta["byte_length"], meta["char_length"])


    def test_deterministic_inverse_multilingual(self):
        for s in ["hello", "नमस्ते", "నమస్కారం", "a" * 40]:
            recovered, ok = deterministic_roundtrip(s)
            self.assertTrue(ok, f"failed for {s!r} -> {recovered!r}")


class TestCollisions(unittest.TestCase):
    def test_collision_detector(self):
        strings = ["ab", "ab", "cd"]
        r = find_collisions(strings, lambda s: s)
        self.assertGreater(r["collision_groups"], 0)


class TestReconstruction(unittest.TestCase):
    def test_exact_match_metric(self):
        r = reconstruction_report("abc", "abc")
        self.assertTrue(r["string_exact_match"])
        r2 = reconstruction_report("abc", "abd")
        self.assertFalse(r2["string_exact_match"])


if __name__ == "__main__":
    unittest.main()
