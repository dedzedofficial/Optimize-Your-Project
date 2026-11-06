"""Regression tests for material and loop provenance validation."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "Blender" / "vr_optimizer_blender" / "preview_attributes.py"
spec = importlib.util.spec_from_file_location("preview_attributes", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PreviewAttributeTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(
            source_faces=[(0, 1, 2), (0, 2, 3)],
            output_faces=[(0, 1, 2, 3)],
            provenance=[(0, 1)],
            source_materials=[4, 4],
            output_materials=[4],
            source_corners=[("a", "b", "c"), ("a", "c", "d")],
            output_corners=[("a", "b", "c", "d")],
        )

    def test_valid_corner_and_material_transfer(self):
        self.assertTrue(module.validate_preview_attributes(**self.args))

    def test_rejects_material_boundary(self):
        args = dict(self.args, source_materials=[4, 5])
        with self.assertRaisesRegex(ValueError, "Material"):
            module.validate_preview_attributes(**args)

    def test_rejects_uv_or_normal_seam(self):
        args = dict(self.args, source_corners=[
            ("a", "b", "c"), ("different", "c", "d")])
        with self.assertRaisesRegex(ValueError, "Incompatible"):
            module.validate_preview_attributes(**args)

    def test_rejects_changed_output_corner(self):
        args = dict(self.args, output_corners=[("a", "b", "changed", "d")])
        with self.assertRaisesRegex(ValueError, "Loop"):
            module.validate_preview_attributes(**args)

    def test_rejects_missing_or_repeated_sources(self):
        for provenance in ([(0,)], [(0, 0)], [(1, 1)]):
            with self.subTest(provenance=provenance):
                with self.assertRaises(ValueError):
                    module.validate_preview_attributes(
                        **dict(self.args, provenance=provenance))

    def test_rejects_invalid_corner_count(self):
        with self.assertRaisesRegex(ValueError, "corner"):
            module.validate_preview_attributes(
                **dict(self.args, output_corners=[("a", "b")]))


if __name__ == "__main__":
    unittest.main()
