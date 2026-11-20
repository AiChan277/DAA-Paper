"""
transit_graph.py
----------------
Loads the weighted Surakarta transit graph G = (V, E, W) from nodes.csv and
edges.csv and provides helpers to evaluate a path (distance, hops, transfers).

Edges are stored as an undirected multigraph: two stops can be joined by more
than one corridor (e.g. Gladag-Benteng Vastenburg is served by K1 and K3).
"""
import csv
import math
from dataclasses import dataclass, field

R_EARTH_KM = 6371.0088
WALK = "WALK"


def haversine_km(lat1, lon1, lat2, lon2):
    """Equation (1): great-circle distance in kilometres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlmb = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(math.sqrt(h))


@dataclass
class TransitGraph:
    name: dict = field(default_factory=dict)        # node_id -> stop name
    lat: dict = field(default_factory=dict)
    lon: dict = field(default_factory=dict)
    adj: dict = field(default_factory=dict)         # node_id -> [(nbr, km, corridor)]
    nbrs: dict = field(default_factory=dict)        # node_id -> [nbr] (unique, ordered)
    w: dict = field(default_factory=dict)           # (u, v) -> min km over corridors
    corridors: dict = field(default_factory=dict)   # (u, v) -> [corridors]
    by_name: dict = field(default_factory=dict)     # stop name -> node_id

    # ------------------------------------------------------------------ load
    @classmethod
    def from_csv(cls, nodes_path, edges_path):
        g = cls()
        with open(nodes_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                i = int(r["node_id"])
                g.name[i] = r["stop_name"]
                g.lat[i], g.lon[i] = float(r["lat"]), float(r["lon"])
                g.adj[i], g.nbrs[i] = [], []
                g.by_name[r["stop_name"]] = i
        with open(edges_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                u, v, d, c = int(r["from_id"]), int(r["to_id"]), float(r["distance_km"]), r["corridor"]
                for a, b in ((u, v), (v, u)):
                    g.adj[a].append((b, d, c))
                    if b not in g.nbrs[a]:
                        g.nbrs[a].append(b)
                    g.w[(a, b)] = min(d, g.w.get((a, b), math.inf))
                    g.corridors.setdefault((a, b), []).append(c)
        return g

    # --------------------------------------------------------------- helpers
    def id(self, stop_name):
        return self.by_name[stop_name]

    def straight_km(self, u, v):
        """Lower bound used by Branch and Bound (straight-line distance)."""
        return haversine_km(self.lat[u], self.lon[u], self.lat[v], self.lon[v])

    @property
    def n_nodes(self):
        return len(self.name)

    @property
    def n_edges(self):
        return sum(len(a) for a in self.adj.values()) // 2

    # ------------------------------------------------------ path evaluation
    def path_distance(self, path):
        """Equation (2): total cost = sum of w(v_i, v_{i+1}) in km."""
        return sum(self.w[(a, b)] for a, b in zip(path, path[1:]))

    def assign_corridors(self, path):
        """Choose one corridor per edge so that the number of transfers is
        minimal (dynamic programming over the corridor labels of each edge).
        Walking links are not boardings, so they never count as a transfer by
        themselves. Returns (transfers, [corridor per edge])."""
        if len(path) < 2:
            return 0, []
        INF = math.inf
        # state: last *ridden* corridor (None before the first boarding)
        layers = [{None: (0, [])}]
        for a, b in zip(path, path[1:]):
            options = sorted(set(self.corridors[(a, b)]))
            nxt = {}
            for last, (cost, seq) in layers[-1].items():
                for c in options:
                    if c == WALK:
                        key, add = last, 0
                    else:
                        key, add = c, (1 if last is not None and c != last else 0)
                    cand = (cost + add, seq + [c])
                    if cand[0] < nxt.get(key, (INF, None))[0]:
                        nxt[key] = cand
            layers.append(nxt)
        best = min(layers[-1].values(), key=lambda x: x[0])
        return best[0], best[1]

    def count_transfers(self, corridor_seq):
        """Transfers in an explicit corridor sequence (walking ignored)."""
        rides = [c for c in corridor_seq if c != WALK]
        return sum(1 for x, y in zip(rides, rides[1:]) if x != y)

    def describe(self, path, corridor_seq=None):
        if corridor_seq is None:
            _, corridor_seq = self.assign_corridors(path)
        legs, start = [], 0
        for i in range(1, len(corridor_seq) + 1):
            if i == len(corridor_seq) or corridor_seq[i] != corridor_seq[start]:
                legs.append(f"{corridor_seq[start]}: {self.name[path[start]]} -> {self.name[path[i]]}")
                start = i
        return " | ".join(legs)
