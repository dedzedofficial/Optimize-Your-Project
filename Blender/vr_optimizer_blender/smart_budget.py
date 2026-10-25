# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic, engine-independent whole-model triangle budget allocation.

Each mesh receives a hard maximum, including a minimum allowance for each
connected surface island. This module deliberately has no Blender dependency,
so budget failures can be tested without starting Blender.
"""

def allocate_triangle_budgets(meshes, triangle_limit):
    """Return per-mesh triangle ceilings, in the same order as *meshes*.

    meshes is a sequence of (triangle_count, connected_island_count) pairs.
    Source geometry must have at least one face and one connected island.
    Each island reserves up to four triangles (or the original number when
    lower). If a global limit cannot cover those minimums, fail explicitly.
    """
    if not meshes:
        raise ValueError("No mesh geometry selected for retopology.")
    if triangle_limit < 1:
        raise ValueError("Triangle limit must be positive.")
    counts = []
    minimums = []
    for count, islands in meshes:
        if count < 1 or islands < 1:
            raise ValueError("Every selected mesh must contain usable faces.")
        counts.append(int(count))
        minimums.append(min(int(count), max(4, 4 * int(islands))))

    required = sum(minimums)
    if required > triangle_limit:
        raise ValueError(
            f"Triangle limit {triangle_limit:,} cannot preserve all "
            f"mesh components (minimum {required:,} triangles). "
            "Raise the limit or choose a smaller model scope."
        )

    original_total = sum(counts)
    if original_total <= triangle_limit:
        # Never manufacture triangles simply to spend unused budget.
        return counts

    remaining = int(triangle_limit) - required
    capacity = [count - minimum for count, minimum in zip(counts, minimums)]
    capacity_sum = sum(capacity)
    if capacity_sum <= 0:
        return minimums

    # Hamilton/largest-remainder apportionment: integer, deterministic and
    # exact, including for hundreds of small mesh components.
    grants = [(remaining * room) // capacity_sum for room in capacity]
    undistributed = remaining - sum(grants)
    residual_order = sorted(
        range(len(counts)),
        key=lambda i: (-(remaining * capacity[i]) % capacity_sum, i),
    )
    for i in residual_order:
        if not undistributed:
            break
        if grants[i] < capacity[i]:
            grants[i] += 1
            undistributed -= 1
    result = [minimum + grant for minimum, grant in zip(minimums, grants)]
    if any(value < minimum or value > count for value, minimum, count
           in zip(result, minimums, counts)):
        raise RuntimeError("Triangle budget allocation exceeded a component bound.")
    if sum(result) > triangle_limit:
        raise RuntimeError("Triangle budget allocation exceeded the global limit.")
    return result
