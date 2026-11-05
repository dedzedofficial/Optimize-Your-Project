"""No-Blender tests for conservative, seam-aware pairing candidates."""
import importlib.util
from pathlib import Path
import unittest

FILE = (Path(__file__).resolve().parents[1] / "Blender" /
        "vr_optimizer_blender" / "triangle_pair_preview.py")
spec = importlib.util.spec_from_file_location("triangle_pair_preview", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PairPreviewTests(unittest.TestCase):
    def setUp(self):
        self.vertices = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
        self.faces = [(0, 1, 2), (0, 2, 3)]

    def test_valid_pair_and_protected_edge(self):
        self.assertEqual(module.propose_pairs(self.vertices, self.faces),
                         [(0, 1, (0, 2))])
        self.assertEqual(module.propose_pairs(
            self.vertices, self.faces, protected_edges={(2, 0)}), [])

    def test_uv_seam_and_material_boundary(self):
        signatures = [((0, 0), (1, 0), (1, 1)),
                      ((0.2, 0), (1, 1), (0, 1))]
        self.assertEqual(module.propose_pairs(
            self.vertices, self.faces, corner_signatures=signatures), [])
        self.assertEqual(module.propose_pairs(
            self.vertices, self.faces, materials=[0, 1]), [])
        signatures[1] = ((0, 0), (1, 1), (0, 1))
        self.assertEqual(len(module.propose_pairs(
            self.vertices, self.faces, corner_signatures=signatures)), 1)

    def test_reject_folded_or_reversed(self):
        folded = [(0, 1, 2), (0, 3, 2)]
        self.assertEqual(module.propose_pairs(self.vertices, folded), [])
        same_winding = [(0, 1, 2), (2, 3, 0)]
        self.assertEqual(len(module.propose_pairs(
            self.vertices, same_winding)), 1)

    def test_reject_invalid_geometry(self):
        with self.assertRaises(ValueError):
            module.propose_pairs(self.vertices, [(0, 0, 2)])
        with self.assertRaises(ValueError):
            module.propose_pairs(self.vertices, self.faces, materials=[0])
        with self.assertRaises(ValueError):
            module.propose_pairs(self.vertices, self.faces, minimum_dot=float("nan"))

    def test_concave_and_collinear_quads_rejected(self):
        concave = [(0, 0, 0), (2, 0, 0), (0.5, 0.2, 0), (0, 2, 0)]
        self.assertEqual(module.propose_pairs(concave, self.faces), [])
        collinear = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0)]
        self.assertEqual(module.propose_pairs(collinear, self.faces), [])

    def test_nonmanifold_edge_not_paired(self):
        vertices = self.vertices + [(0.5, 0.5, 1)]
        faces = self.faces + [(0, 2, 4)]
        self.assertEqual(module.propose_pairs(vertices, faces), [])


if __name__ == "__main__":
    unittest.main()
