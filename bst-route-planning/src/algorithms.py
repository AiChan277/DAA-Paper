"""
algorithms.py
-------------
Route-search algorithms compared in the study. Every function returns a
SearchResult with the path found and the instrumentation counters used in the
paper:

  visited_nodes : number of nodes (states for B&B with a transfer penalty)
                  expanded, i.e. removed from the frontier and processed
  peak_frontier : BFS -> maximum queue length
                  DFS -> maximum recursion depth (call-stack frames)
                  B&B / Dijkstra -> maximum priority-queue length
  pruned        : branches cut by the bound (B&B only)

Theoretical complexity (V = stops, E = edges):
  BFS        time O(|V| + |E|)            space O(|V|)
  DFS        time O(|V| + |E|)            space O(|V|) (recursion depth)
  Dijkstra   time O((|V| + |E|) log |V|)  space O(|V|)
  LC-B&B     worst case as Dijkstra on the state space; the bound
             f = g + straight-line(u, goal) prunes branches that cannot beat
             the incumbent, so far fewer nodes are expanded in practice.
"""
import heapq
import itertools
import math
import sys
from collections import deque
from dataclasses import dataclass, field

from transit_graph import WALK

sys.setrecursionlimit(10_000)


@dataclass
class SearchResult:
    algorithm: str
    path: list
    corridor_seq: list = field(default_factory=list)  # set for state-space B&B
    visited_nodes: int = 0
    peak_frontier: int = 0
    pruned: int = 0
    found: bool = True


# ---------------------------------------------------------------------------
# 1. Breadth-First Search: minimum number of hops (stops)
# ---------------------------------------------------------------------------
def bfs(g, source, target):
    parent = {source: None}
    queue = deque([source])
    expanded, peak = 0, 1
    while queue:
        u = queue.popleft()
        expanded += 1
        if u == target:
            break
        for v in g.nbrs[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
        if len(queue) > peak:
            peak = len(queue)
    if target not in parent:
        return SearchResult("BFS", [], visited_nodes=expanded, peak_frontier=peak, found=False)
    path, x = [], target
    while x is not None:
        path.append(x)
        x = parent[x]
    return SearchResult("BFS", path[::-1], visited_nodes=expanded, peak_frontier=peak)


# ---------------------------------------------------------------------------
# 2. Depth-First Search (recursive): first path found
# ---------------------------------------------------------------------------
def dfs(g, source, target, neighbour_order=None):
    """neighbour_order: optional dict node -> list of neighbours, used only for
    the order-sensitivity experiment; default is the order of edges.csv."""
    order = neighbour_order or g.nbrs
    visited, path = set(), []
    stats = {"expanded": 0, "depth": 0}

    def visit(u, depth):
        visited.add(u)
        path.append(u)
        stats["expanded"] += 1
        if depth > stats["depth"]:
            stats["depth"] = depth
        if u == target:
            return True
        for v in order[u]:
            if v not in visited and visit(v, depth + 1):
                return True
        path.pop()
        return False

    found = visit(source, 1)
    return SearchResult("DFS", list(path) if found else [], visited_nodes=stats["expanded"],
                        peak_frontier=stats["depth"], found=found)


# ---------------------------------------------------------------------------
# 3. Least-Cost Branch and Bound: minimum physical distance (km)
# ---------------------------------------------------------------------------
def branch_and_bound(g, source, target, transfer_penalty_km=0.0):
    """Best-first (least-cost) branch and bound.

    Each live node is a partial route with cost g (km travelled, plus
    transfer_penalty_km per corridor change). Its bound is
        f = g + straight_line_km(u, target),
    a valid lower bound because every edge weight is at least the straight-line
    distance between its end stops (circuity factor >= 1) and straight-line
    distance obeys the triangle inequality. A branch is pruned when
        f >= best complete route found so far (the incumbent), or
        g >= the best cost already recorded for the same state (dominance).
    The search stops when the smallest bound in the queue cannot beat the
    incumbent, so the returned route is guaranteed optimal.

    With transfer_penalty_km = 0 the state is the stop alone. With a positive
    penalty the state is (stop, last corridor ridden), so transfers can be
    charged exactly.
    """
    use_state = transfer_penalty_km > 0
    h_cache = {}

    def h(u):                       # lower bound, cached per query
        val = h_cache.get(u)
        if val is None:
            val = h_cache[u] = g.straight_km(u, target)
        return val
    start = (source, None)
    best_cost, best_state = math.inf, None
    best_g = {start: 0.0}
    parent = {start: (None, None)}
    tie = itertools.count()
    pq = [(h(source), 0.0, next(tie), start)]
    expanded = pruned = 0
    peak = 1
    expanded_stops = set()
    while pq:
        f, cost, _, state = heapq.heappop(pq)
        if f >= best_cost:          # bound: nothing left can improve the incumbent
            pruned += 1 + len(pq)
            break
        if cost > best_g.get(state, math.inf):
            continue                # stale queue entry
        u, last = state
        expanded += 1
        expanded_stops.add(u)
        if u == target:
            best_cost, best_state = cost, state
            continue
        for v, w, c in g.adj[u]:
            if use_state:
                if c == WALK:
                    nlast, pen = last, 0.0
                else:
                    nlast = c
                    pen = transfer_penalty_km if (last is not None and c != last) else 0.0
                nstate = (v, nlast)
            else:
                pen, nstate = 0.0, (v, None)
            ncost = cost + w + pen
            if ncost + h(v) >= best_cost or ncost >= best_g.get(nstate, math.inf):
                pruned += 1
                continue
            best_g[nstate] = ncost
            parent[nstate] = (state, c)
            heapq.heappush(pq, (ncost + h(v), ncost, next(tie), nstate))
        if len(pq) > peak:
            peak = len(pq)
    if best_state is None:
        return SearchResult("B&B", [], visited_nodes=expanded, peak_frontier=peak,
                            pruned=pruned, found=False)
    path, cseq, s = [], [], best_state
    while s is not None:
        path.append(s[0])
        prev, c = parent[s]
        if c is not None:
            cseq.append(c)
        s = prev
    name = "B&B" if not use_state else f"B&B(pen={transfer_penalty_km:g})"
    return SearchResult(name, path[::-1], corridor_seq=cseq[::-1] if use_state else [],
                        visited_nodes=len(expanded_stops) if not use_state else expanded,
                        peak_frontier=peak, pruned=pruned)


# ---------------------------------------------------------------------------
# Reference: Dijkstra (used to validate that B&B returns the optimum)
# ---------------------------------------------------------------------------
def dijkstra(g, source, target):
    dist = {source: 0.0}
    parent = {source: None}
    done = set()
    tie = itertools.count()
    pq = [(0.0, next(tie), source)]
    peak = 1
    while pq:
        d, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        if u == target:
            break
        for v in g.nbrs[u]:
            nd = d + g.w[(u, v)]
            if nd < dist.get(v, math.inf):
                dist[v], parent[v] = nd, u
                heapq.heappush(pq, (nd, next(tie), v))
        if len(pq) > peak:
            peak = len(pq)
    if target not in parent:
        return SearchResult("Dijkstra", [], visited_nodes=len(done), peak_frontier=peak, found=False)
    path, x = [], target
    while x is not None:
        path.append(x)
        x = parent[x]
    return SearchResult("Dijkstra", path[::-1], visited_nodes=len(done), peak_frontier=peak)
