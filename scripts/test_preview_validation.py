"""Standalone regression tests for conservative preview validation."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "Blender" / "vr_optimizer_blender" / "preview_validation.py"
spec = importlib.util.spec_from_file_location("preview_validation", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PreviewValidationTests(unittest.TestCase):
    def setUp(self):
        self.source = [(0, 1, 2), (0, 2, 3)]
        self.preview = [(0, 1, 2, 3)]
        self.sources = [(0, 1)]

    def test_valid_join(self):
        self.assertTrue(module.validate_preview(self.source, self.preview, self.sources))

    def test_rejects_missing_or_reused_source(self):
        for provenance in ([(0,)], [(0, 0)], [(0, 2)]):
            with self.subTest(provenance=provenance):
                with self.assertRaises(ValueError):
                    module.validate_preview(self.source, self.preview, provenance)

    def test_rejects_bad_quad_or_changed_boundary(self):
        for face in ((0, 1, 3, 2), (0, 1, 2, 4), (0, 1, 2)):
            with self.subTest(face=face):
                with self.assertRaises(ValueError):
                    module.validate_preview(self.source, [face], self.sources)

    def test_rejects_reversed_quad_winding(self):
        with self.assertRaisesRegex(ValueError, "winding"):
            module.validate_preview(self.source, [(0, 3, 2, 1)], self.sources)

    def test_accepts_rotated_quad_start(self):
        self.assertTrue(module.validate_preview(self.source, [(2, 3, 0, 1)], self.sources))

    def test_rejects_unpaired_changes(self):
        with self.assertRaises(ValueError):
            module.validate_preview(self.source, [(1, 0, 2), self.source[1]], [(0,), (1,)])

    def test_rejects_nonmanifold_incidence_change(self):
        source = [(0, 1, 2), (0, 2, 3), (0, 2, 4)]
        with self.assertRaises(ValueError):
            module.validate_preview(source, [(0, 1, 2, 3), (0, 2, 4)], [(0, 1), (2,)])


if __name__ == "__main__":
    unittest.main()
