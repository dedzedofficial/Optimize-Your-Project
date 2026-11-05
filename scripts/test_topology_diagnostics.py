"""Standalone regression checks for retopology topology diagnostics."""
import importlib.util
from pathlib import Path
import unittest

FILE = (Path(__file__).resolve().parents[1] / "Blender" /
        "vr_optimizer_blender" / "topology_diagnostics.py")
spec = importlib.util.spec_from_file_location("topology_diagnostics", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TopologyGateTests(unittest.TestCase):
    def test_single_quad(self):
        report = module.analyze_faces(4, [(0, 1, 2, 3)])
        self.assertEqual(report["quads"], 1)
        self.assertEqual(report["quad_percent"], 100)
        self.assertEqual(report["triangle_equivalents"], 2)
        self.assertEqual(report["boundary_edges"], 4)
        self.assertEqual(report["components"], 1)

    def test_triangle_pair(self):
        before = module.analyze_faces(4, [(0, 1, 2), (0, 2, 3)])
        after = module.analyze_faces(4, [(0, 1, 2, 3)])
        self.assertEqual(before["triangle_equivalents"], after["triangle_equivalents"])
        self.assertEqual(before["boundary_edges"], after["boundary_edges"])
        self.assertEqual(module.compare_topology(before, after), [])

    def test_loose_vertices_and_separate_islands(self):
        result = module.analyze_faces(7, [(0, 1, 2), (3, 4, 5)])
        self.assertEqual(result["components"], 3)
        self.assertEqual(result["loose_vertices"], 1)
        self.assertEqual(result["component_vertex_sizes"], [1, 3, 3])

    def test_nonmanifold(self):
        result = module.analyze_faces(
            5, [(0, 1, 2), (1, 0, 3), (0, 1, 4)])
        self.assertEqual(result["nonmanifold_edges"], 1)

    def test_winding_conflicts_and_valence(self):
        consistent = module.analyze_faces(4, [(0, 1, 2), (0, 2, 3)])
        flipped = module.analyze_faces(4, [(0, 1, 2), (3, 2, 0)])
        self.assertEqual(consistent["winding_conflict_edges"], 0)
        self.assertEqual(flipped["winding_conflict_edges"], 1)
        self.assertEqual(consistent["high_valence_vertices"], 0)
        fan = module.analyze_faces(9, [
            (0, 1, 5, 4), (1, 2, 6, 5),
            (4, 5, 7, 8), (5, 6, 3, 7)])
        self.assertGreaterEqual(fan["valence_four_vertices"], 1)

    def test_budget_and_quad_gate(self):
        source = module.analyze_faces(4, [(0, 1, 2), (0, 2, 3)])
        failures = module.compare_topology(
            source, source, max_triangles=1, minimum_quad_percent=90)
        self.assertIn("triangle budget exceeded", failures)
        self.assertIn("quad percentage below target", failures)

    def test_rejects_component_loss(self):
        before = module.analyze_faces(6, [(0, 1, 2), (3, 4, 5)])
        after = module.analyze_faces(6, [(0, 1, 2), (2, 3, 4)])
        self.assertIn("vertex-connected component structure changed",
                      module.compare_topology(before, after))

    def test_retessellation_can_change_component_vertex_sizes(self):
        before = module.analyze_faces(4, [(0, 1, 2, 3)])
        after = module.analyze_faces(5, [(0, 1, 4, 3), (1, 2, 4)])
        self.assertEqual(module.compare_topology(
            before, after, preserve_boundary=False), [])
        self.assertIn("vertex-connected component structure changed",
                      module.compare_topology(
                          before, after, preserve_boundary=False,
                          preserve_component_sizes=True))

    def test_rejects_loose_vertex_change(self):
        before = module.analyze_faces(5, [(0, 1, 2)])
        after = module.analyze_faces(5, [(0, 1, 2), (2, 3, 4)])
        self.assertIn("loose vertex count changed",
                      module.compare_topology(before, after))

    def test_invalid_thresholds(self):
        report = module.analyze_faces(3, [(0, 1, 2)])
        for value in (float("nan"), float("inf"), -1, True):
            with self.assertRaises(ValueError):
                module.compare_topology(report, report, max_triangles=value)
        for value in (float("nan"), 101, -1, True):
            with self.assertRaises(ValueError):
                module.compare_topology(report, report,
                                        minimum_quad_percent=value)

    def test_rejects_bad_indices(self):
        for faces in [[(0, 1, 9)], [(0, 0, 1)], [(0, 1)], [(-1, 1, 2)], [(0, 1, True)]]:
            with self.assertRaises(ValueError):
                module.analyze_faces(3, faces)


    def test_component_reports_are_isolated_and_deterministic(self):
        faces = [(3, 4, 5, 6), (0, 1, 2)]
        parts = module.analyze_components(8, faces)
        self.assertEqual([part["first_vertex"] for part in parts], [0, 3, 7])
        self.assertEqual([part["vertices"] for part in parts], [3, 4, 1])
        self.assertEqual([part["quads"] for part in parts], [0, 1, 0])
        self.assertEqual([part["triangle_equivalents"] for part in parts], [1, 2, 0])
        self.assertEqual([part["boundary_edges"] for part in parts], [3, 4, 0])
        self.assertEqual(sum(p["triangle_equivalents"] for p in parts), 3)
        self.assertEqual(parts, module.analyze_components(8, list(reversed(faces))))

    def test_component_reports_reject_invalid_faces(self):
        for faces in ([(0, 1, 3)], [(0, 1, 1)], [(0, True, 2)]):
            with self.assertRaises(ValueError):
                module.analyze_components(3, faces)

if __name__ == "__main__":
    unittest.main()
