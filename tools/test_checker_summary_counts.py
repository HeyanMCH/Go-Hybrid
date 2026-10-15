"""Verify checker error-count metadata against diagnostics (offline)."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "corpus_harness", Path(__file__).with_name("corpus_harness.py")
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class CheckerSummaryCountsTests(TestCase):
    def run_checker(self, verdict, count, diagnostics, *, include_count=True):
        summary = {"verdict": verdict}
        if include_count:
            summary["errors"] = count
        proc = SimpleNamespace(
            returncode=0 if verdict == "accept" else 1,
            stdout=json.dumps({"summary": summary, "diagnostics": diagnostics}),
            stderr="",
        )
        with patch.object(harness.subprocess, "run", return_value=proc):
            return harness.run_checker("hyb", "case.hy")

    def test_false_clean_accept_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "checker error count mismatch"):
            self.run_checker("accept", 1, [])

    def test_false_clean_reject_is_rejected(self):
        errors = [{"severity": "error", "tier0_rule": "A1b"}]
        with self.assertRaisesRegex(RuntimeError, "checker error count mismatch"):
            self.run_checker("reject", 0, errors)

    def test_clean_accept_remains_valid(self):
        summary, diags = self.run_checker("accept", 0, [])
        self.assertEqual(summary["verdict"], "accept")
        self.assertEqual(diags, [])

    def test_correct_rejection_remains_valid(self):
        errors = [{"severity": "error", "tier0_rule": "A1b"}]
        _, diags = self.run_checker("reject", 1, errors)
        self.assertEqual(diags, errors)

    def test_missing_legacy_count_is_tolerated(self):
        _, diags = self.run_checker("accept", None, [], include_count=False)
        self.assertEqual(diags, [])

    def test_boolean_count_is_not_an_integer_count(self):
        with self.assertRaisesRegex(RuntimeError, "checker error count mismatch"):
            self.run_checker("reject", True, [{"severity": "error"}])


if __name__ == "__main__":
    main()
