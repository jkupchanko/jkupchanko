"""A real (small) HNSW index, laid out for drawing.

Nothing here is decorative. Layers are nested subsets the way HNSW promotes
nodes, edges are M-nearest plus long-range links, and the traversal is an
actual greedy descent. Every number printed on the hero comes out of this.

Points live in an aspect-corrected unit box (ASPECT wide, 1 tall) so that
"nearest neighbour" means nearest *as drawn* - in a band that is 16x wider
than it is tall, unit-space nearest would produce edges that look wrong.
"""
import math
import random

ASPECT = 16.75         # band width : band height, matches the hero geometry


class Node:
    __slots__ = ("idx", "u", "v", "x", "y", "nbrs")

    def __init__(self, idx, u, v):
        self.idx = idx
        self.u = u          # 0..ASPECT
        self.v = v          # 0..1
        self.x = 0.0
        self.y = 0.0
        self.nbrs = []

    def d(self, other):
        return math.hypot(self.u - other.u, self.v - other.v)


def best_candidate(n, rng, tries=12):
    """Mitchell's best-candidate scatter: even, but not a lattice.

    Uniform random clumps and a grid reads as a ruler. This sits between the
    two, which is what a projected index actually looks like.
    """
    pts = [(rng.uniform(0, ASPECT), rng.uniform(0, 1))]
    while len(pts) < n:
        best, best_d = None, -1.0
        for _ in range(tries):
            c = (rng.uniform(0, ASPECT), rng.uniform(0, 1))
            d = min(math.hypot(c[0] - q[0], c[1] - q[1]) for q in pts)
            if d > best_d:
                best, best_d = c, d
        pts.append(best)
    pts.sort()
    return pts


def build_layer(pts, m, rng, highways=0.18):
    nodes = [Node(i, u, v) for i, (u, v) in enumerate(pts)]
    for a in nodes:
        order = sorted(nodes, key=a.d)
        for b in order[1 : m + 1]:
            if b.idx not in a.nbrs:
                a.nbrs.append(b.idx)
            if a.idx not in b.nbrs:
                b.nbrs.append(a.idx)
    # long-range links - the "highway" edges that give HNSW its log-ish hops
    far = ASPECT / 5.0
    for _ in range(int(len(nodes) * highways)):
        a = rng.choice(nodes)
        cands = [b for b in nodes if abs(b.u - a.u) > far]
        if not cands:
            continue
        b = rng.choice(cands)
        if b.idx not in a.nbrs:
            a.nbrs.append(b.idx)
            b.nbrs.append(a.idx)
    return nodes


def greedy(nodes, entry, q):
    """Greedy best-first descent. Returns the visited node sequence."""
    cur, path, seen = entry, [entry], {entry}
    while True:
        best = cur
        best_d = math.hypot(nodes[cur].u - q[0], nodes[cur].v - q[1])
        for nb in nodes[cur].nbrs:
            d = math.hypot(nodes[nb].u - q[0], nodes[nb].v - q[1])
            if d < best_d:
                best, best_d = nb, d
        if best == cur or best in seen:
            return path
        cur = best
        seen.add(cur)
        path.append(cur)


def build(seed=96, sizes=(200, 36, 9), m=(3, 2, 2), query=(12.9, 0.42)):
    rng = random.Random(seed)
    base = best_candidate(sizes[0], rng)

    layer_pts = [base]
    for n in sizes[1:]:
        layer_pts.append(sorted(rng.sample(layer_pts[-1], n)))

    layers = [build_layer(pts, m[i], rng) for i, pts in enumerate(layer_pts)]

    top = len(layers) - 1
    # enter far from the query, on the left, so the descent actually travels
    entry = min(range(len(layers[top])),
                key=lambda i: math.hypot(layers[top][i].u - 0.6, layers[top][i].v - 0.5))

    routes = []
    for lv in range(top, -1, -1):
        nodes = layers[lv]
        path = greedy(nodes, entry, query)
        routes.append(path)
        if lv > 0:
            land = nodes[path[-1]]
            below = layers[lv - 1]
            entry = min(range(len(below)), key=lambda i: below[i].d(land))

    landed = layers[0][routes[-1][-1]]
    true_best = min(layers[0], key=lambda n: math.hypot(n.u - query[0], n.v - query[1]))
    d_land = math.hypot(landed.u - query[0], landed.v - query[1])
    d_true = math.hypot(true_best.u - query[0], true_best.v - query[1])

    return {
        "layers": layers,
        "routes": routes,
        "query": query,
        "hops": sum(len(r) - 1 for r in routes) + (len(layers) - 1),
        "landed": landed,
        "exact": true_best,
        "hit": landed is true_best,
        "ratio": (d_land / d_true) if d_true else 1.0,
        "edges": sum(len(n.nbrs) for lv in layers for n in lv) // 2,
        "nodes": sum(len(lv) for lv in layers),
    }


if __name__ == "__main__":
    ix = build()
    for lv, layer in enumerate(ix["layers"]):
        print("L%d: %4d nodes, %4d edges" % (lv, len(layer), sum(len(n.nbrs) for n in layer) // 2))
    print("routes :", [len(r) for r in ix["routes"]])
    print("hops   :", ix["hops"], " hit:", ix["hit"], " ratio: %.4f" % ix["ratio"])
