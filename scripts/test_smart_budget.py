"""Standalone budget tests; run with python3 scripts/test_smart_budget.py."""
import sys
import unittest
from pathlib import Path

import importlib.util

module_path = (Path(__file__).resolve().parents[1]
               / "Blender" / "vr_optimizer_blender" / "smart_budget.py")
spec = importlib.util.spec_from_file_location("smart_budget", module_path)
budget_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(budget_module)
allocate_triangle_budgets = budget_module.allocate_triangle_budgets


class TriangleBudgetTests(unittest.TestCase):
    def test_entire_model_stays_inside_global_limit(self):
        result = allocate_triangle_budgets([(12000, 1), (8000, 1), (5000, 2)], 4000)
        self.assertEqual(sum(result), 4000)
        self.assertTrue(all(value >= 4 for value in result))

    def test_budget_distributes_with_minimum_per_island(self):
        result = allocate_triangle_budgets([(300, 10), (800, 1), (200, 3)], 100)
        self.assertEqual(sum(result), 100)
        self.assertGreaterEqual(result[0], 40)
        self.assertGreaterEqual(result[1], 4)
        self.assertGreaterEqual(result[2], 12)

    def test_no_inflation_under_budget(self):
        self.assertEqual(
            allocate_triangle_budgets([(12, 1), (80, 2)], 1000), [12, 80])

    def test_impossible_budget_refuses(self):
        with self.assertRaisesRegex(ValueError, "cannot preserve"):
            allocate_triangle_budgets([(30, 4), (30, 5)], 12)

    def test_tiny_meshes_keep_at_least_existing_triangles(self):
        self.assertEqual(
            allocate_triangle_budgets([(1, 1), (2, 1), (10, 1)], 8), [1, 2, 5])

    def test_repeatable_allocation(self):
        meshes = [(700, 3), (700, 3), (701, 2), (70, 1)]
        first = allocate_triangle_budgets(meshes, 121)
        for _ in range(20):
            self.assertEqual(allocate_triangle_budgets(meshes, 121), first)
        self.assertEqual(sum(first), 121)

    def test_reject_empty_input(self):
        with self.assertRaises(ValueError):
            allocate_triangle_budgets([], 100)

    def test_many_components(self):
        meshes = [(150, 1)] * 40
        self.assertEqual(sum(allocate_triangle_budgets(meshes, 500)), 500)


if __name__ == "__main__":
    unittest.main()
