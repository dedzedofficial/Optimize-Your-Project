"""Regression tests for the integrated, non-destructive preview gate."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

root = Path(__file__).resolve().parents[1] / "Blender" / "vr_optimizer_blender"
package = types.ModuleType("_preview_test_package")
package.__path__ = [str(root)]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location(
    package.__name__ + ".validated_pair_preview",
    root / "validated_pair_preview.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class IntegratedPreviewTests(unittest.TestCase):
    def setUp(self):
        self.vertices = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
        self.faces = [(0, 1, 2), (0, 2, 3)]
        self.materials = [2, 2]
        self.corners = [("a", "b", "c"), ("a", "c", "d")]

    def run_preview(self, **overrides):
        args = dict(materials=self.materials, corner_signatures=self.corners)
        args.update(overrides)
        return module.validated_pair_preview(self.vertices, self.faces, **args)

    def test_valid_preview_and_immutable_inputs(self):
        before = (list(self.vertices), list(self.faces), list(self.materials),
                  list(self.corners))
        result = self.run_preview()
        self.assertEqual(result["quad_joins"], 1)
        self.assertEqual(result["paired_triangles"], 2)
        self.assertEqual(result["source_faces"], 2)
        self.assertEqual(result["output_faces"], 1)
        self.assertEqual(result["source_triangle_equivalents"], 2)
        self.assertEqual(result["output_triangle_equivalents"], 2)
        self.assertEqual(result["materials"], [2])
        self.assertEqual(before, (self.vertices, self.faces, self.materials,
                                  self.corners))

    def test_rejects_omitted_protected_layers(self):
        for override in (dict(materials=None), dict(corner_signatures=None)):
            with self.subTest(override=override):
                with self.assertRaisesRegex(ValueError, "required"):
                    self.run_preview(**override)

    def test_material_boundary_blocks_join(self):
        result = self.run_preview(materials=[2, 3])
        self.assertEqual(result["quad_joins"], 0)
        self.assertEqual(result["output_faces"], 2)
        self.assertEqual(result["materials"], [2, 3])

    def test_uv_seam_blocks_join(self):
        result = self.run_preview(corner_signatures=[
            ("a", "b", "c"), ("seam", "c", "d")])
        self.assertEqual(result["quad_joins"], 0)

    def test_protected_edge_blocks_join(self):
        result = self.run_preview(protected_edges=[(0, 2)])
        self.assertEqual(result["quad_joins"], 0)

    def test_invalid_source_layers_rejected(self):
        with self.assertRaisesRegex(ValueError, "count"):
            self.run_preview(materials=[2])


if __name__ == "__main__":
    unittest.main()
