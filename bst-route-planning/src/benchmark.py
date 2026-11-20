"""
benchmark.py
------------
Runs BFS, DFS and Least-Cost Branch and Bound (plus Dijkstra as an optimality
reference) on 15 Surakarta route scenarios and writes every table used in
Section IV of the paper.

Usage (from the repository root):
    python src/benchmark.py            # full run, writes results/ and figures/
    python src/benchmark.py --reps 50  # quicker run with fewer timing repetitions
"""
import argparse
import csv
import gc
import os
import platform
import random
import statistics
import sys
import time
import tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transit_graph import TransitGraph            # noqa: E402
from algorithms import bfs, dfs, branch_and_bound, dijkstra   # noqa: E402

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(ROOT, "figures")

# 15 route scenarios. Category is fixed by the minimum number of transfers the
# network allows (checked at run time): short = 0, medium = 1, long >= 2.
ROUTES = [
    ("S1", "Short", "Solo Balapan", "Mall Paragon"),
    ("S2", "Short", "Terminal Tirtonadi", "Pasar Legi"),
    ("S3", "Short", "Pasar Gede", "Pasar Klewer"),
    ("S4", "Short", "Stadion Manahan", "Klodran"),
    ("S5", "Short", "Kleco", "Gladag"),
    ("M1", "Medium", "Bandara Adi Soemarmo", "Stadion Manahan"),
    ("M2", "Medium", "Sub Terminal Pelangi Mojosongo", "Solo Balapan"),
    ("M3", "Medium", "Purwosari", "Taman Lansia"),
    ("M4", "Medium", "UNS", "Pasar Klewer"),
    ("M5", "Medium", "RSUD Ngipang", "UNS"),
    ("L1", "Long", "Lapangan Gentan", "Bandara Adi Soemarmo"),
    ("L2", "Long", "Kadipiro", "Klodran"),
    ("L3", "Long", "Goa Maria", "Simpang Sidan"),
    ("L4", "Long", "Tugu Adipura Jurug", "Graha Saba Buana"),
    ("L5", "Long", "RSUD Ngipang", "Pasar Bekonang"),
]
EXPECTED_MIN_TRANSFERS = {"Short": (0, 0), "Medium": (1, 1), "Long": (2, 99)}
ALGORITHMS = [("BFS", bfs), ("DFS", dfs), ("B&B", branch_and_bound), ("Dijkstra", dijkstra)]
PENALTIES_KM = [0.0, 1.0, 2.5, 5.0]
DFS_SHUFFLES = 50


def time_us(fn, reps, warmup=20):
    """Median and 95th-percentile wall-clock time in microseconds."""
    for _ in range(warmup):
        fn()
    samples = []
    gc_was = gc.isenabled()
    gc.disable()
    try:
        for _ in range(reps):
            t0 = time.perf_counter_ns()
            fn()
            samples.append((time.perf_counter_ns() - t0) / 1000.0)
    finally:
        if gc_was:
            gc.enable()
    samples.sort()
    return statistics.median(samples), samples[int(0.95 * (len(samples) - 1))]


def peak_kib(fn):
    tracemalloc.start()
    tracemalloc.reset_peak()
    fn()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024.0


def min_transfers(g, s, t):
    r = branch_and_bound(g, s, t, transfer_penalty_km=1000.0)
    return g.count_transfers(r.corridor_seq)


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300, help="timing repetitions per run")
    args = ap.parse_args()
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(FIGURES, exist_ok=True)

    g = TransitGraph.from_csv(os.path.join(DATA, "nodes.csv"), os.path.join(DATA, "edges.csv"))
    print(f"Graph loaded: |V| = {g.n_nodes}, |E| = {g.n_edges}")

    # ---------------------------------------------------------- scenarios
    scen_rows = []
    for rid, cat, a, b in ROUTES:
        s, t = g.id(a), g.id(b)
        mt = min_transfers(g, s, t)
        lo, hi = EXPECTED_MIN_TRANSFERS[cat]
        assert lo <= mt <= hi, f"{rid} {a}->{b}: min transfers {mt} not valid for {cat}"
        scen_rows.append([rid, cat, a, b, mt, f"{g.straight_km(s, t):.2f}"])
    write_csv(os.path.join(RESULTS, "route_scenarios.csv"),
              ["route_id", "category", "origin", "destination", "min_transfers",
               "straight_line_km"], scen_rows)

    # ------------------------------------------------------- main benchmark
    main_rows, detail = [], {}
    for rid, cat, a, b in ROUTES:
        s, t = g.id(a), g.id(b)
        for alg_name, fn in ALGORITHMS:
            res = fn(g, s, t)
            transfers, cseq = g.assign_corridors(res.path)
            dist = g.path_distance(res.path)
            med, p95 = time_us(lambda: fn(g, s, t), args.reps)
            mem = peak_kib(lambda: fn(g, s, t))
            row = [rid, cat, a, b, alg_name, len(res.path) - 1, f"{dist:.2f}", transfers,
                   res.visited_nodes, res.peak_frontier, res.pruned, f"{med:.1f}", f"{p95:.1f}",
                   f"{mem:.1f}", g.describe(res.path, cseq)]
            main_rows.append(row)
            detail[(rid, alg_name)] = dict(hops=len(res.path) - 1, km=dist, tr=transfers,
                                           visited=res.visited_nodes, peak=res.peak_frontier,
                                           pruned=res.pruned, t=med, mem=mem,
                                           route=g.describe(res.path, cseq))
            print(f"{rid} {alg_name:8s} hops={len(res.path)-1:3d} km={dist:6.2f} tr={transfers} "
                  f"visited={res.visited_nodes:3d} peak={res.peak_frontier:3d} t={med:8.1f}us")
    write_csv(os.path.join(RESULTS, "results_main.csv"),
              ["route_id", "category", "origin", "destination", "algorithm", "hops",
               "distance_km", "transfers", "visited_nodes", "peak_frontier", "pruned",
               "time_us_median", "time_us_p95", "tracemalloc_peak_kib", "route"], main_rows)

    # Optimality check: B&B must equal Dijkstra on every route
    for rid, *_ in ROUTES:
        assert abs(detail[(rid, "B&B")]["km"] - detail[(rid, "Dijkstra")]["km"]) < 1e-9, rid

    # ------------------------------------------------ category summary
    summ_rows = []
    for cat in ("Short", "Medium", "Long", "All"):
        ids = [r[0] for r in ROUTES if cat == "All" or r[1] == cat]
        for alg_name, _ in ALGORITHMS:
            d = [detail[(i, alg_name)] for i in ids]
            opt = [detail[(i, "Dijkstra")]["km"] for i in ids]
            gap = statistics.mean((x["km"] - o) / o * 100 for x, o in zip(d, opt))
            summ_rows.append([cat, alg_name,
                              f"{statistics.mean(x['hops'] for x in d):.1f}",
                              f"{statistics.mean(x['km'] for x in d):.2f}",
                              f"{gap:.1f}",
                              f"{statistics.mean(x['tr'] for x in d):.1f}",
                              f"{statistics.mean(x['visited'] for x in d):.1f}",
                              f"{statistics.mean(x['peak'] for x in d):.1f}",
                              f"{statistics.mean(x['t'] for x in d):.1f}",
                              f"{statistics.mean(x['mem'] for x in d):.1f}"])
    summ_header = ["category", "algorithm", "mean_hops", "mean_km", "mean_km_gap_vs_optimal_pct",
                   "mean_transfers", "mean_visited", "mean_peak_frontier", "mean_time_us",
                   "mean_tracemalloc_kib"]
    write_csv(os.path.join(RESULTS, "summary_by_category.csv"), summ_header, summ_rows)

    # ---------------------------------- B&B with a transfer penalty (km)
    pen_rows = []
    for rid, cat, a, b in ROUTES:
        s, t = g.id(a), g.id(b)
        for pen in PENALTIES_KM:
            r = branch_and_bound(g, s, t, transfer_penalty_km=pen)
            if pen == 0:
                tr, cseq = g.assign_corridors(r.path)
            else:
                cseq = r.corridor_seq
                tr = g.count_transfers(cseq)
            med, _ = time_us(lambda: branch_and_bound(g, s, t, transfer_penalty_km=pen),
                             max(50, args.reps // 3))
            pen_rows.append([rid, cat, f"{pen:g}", len(r.path) - 1,
                             f"{g.path_distance(r.path):.2f}", tr, r.visited_nodes,
                             r.peak_frontier, f"{med:.1f}", g.describe(r.path, cseq)])
    write_csv(os.path.join(RESULTS, "bnb_transfer_penalty.csv"),
              ["route_id", "category", "penalty_km_per_transfer", "hops", "distance_km",
               "transfers", "visited_states", "peak_frontier", "time_us_median", "route"],
              pen_rows)

    # --------------------------- DFS sensitivity to neighbour visiting order
    rng = random.Random(2026)
    sens_rows = []
    for rid, cat, a, b in ROUTES:
        s, t = g.id(a), g.id(b)
        hops, kms = [], []
        for _ in range(DFS_SHUFFLES):
            order = {u: rng.sample(v, len(v)) for u, v in g.nbrs.items()}
            r = dfs(g, s, t, neighbour_order=order)
            hops.append(len(r.path) - 1)
            kms.append(g.path_distance(r.path))
        sens_rows.append([rid, cat, min(hops), f"{statistics.mean(hops):.1f}", max(hops),
                          f"{statistics.pstdev(hops):.1f}", f"{min(kms):.2f}",
                          f"{statistics.mean(kms):.2f}", f"{max(kms):.2f}",
                          detail[(rid, "BFS")]["hops"], f"{detail[(rid, 'B&B')]['km']:.2f}"])
    write_csv(os.path.join(RESULTS, "dfs_order_sensitivity.csv"),
              ["route_id", "category", "dfs_min_hops", "dfs_mean_hops", "dfs_max_hops",
               "dfs_sd_hops", "dfs_min_km", "dfs_mean_km", "dfs_max_km", "bfs_hops",
               "optimal_km"], sens_rows)

    # ----------------------------------------------------- markdown report
    cpu = platform.processor() or "n/a"
    try:
        with open("/proc/cpuinfo") as f:
            cpu = next(l.split(":", 1)[1].strip() for l in f if l.startswith("model name"))
    except (OSError, StopIteration):
        pass
    env = (f"Python {platform.python_version()} ({platform.python_implementation()}), "
           f"{platform.system()} {platform.release()}, {platform.machine()}, "
           f"CPU: {cpu}; timing = median of {args.reps} runs "
           f"after 20 warm-up runs, garbage collector disabled during timing.")
    with open(os.path.join(RESULTS, "environment.txt"), "w") as f:
        f.write(env + "\n")
    md = [f"# Benchmark results\n\nGraph: |V| = {g.n_nodes} stops, |E| = {g.n_edges} edges.\n\n{env}\n",
          "## Route scenarios\n", md_table(["ID", "Category", "Origin", "Destination",
                                            "Min transfers", "Straight-line km"], scen_rows),
          "\n## Per-route results\n"]
    hdr = ["ID", "Alg", "Hops", "km", "Transfers", "Visited", "Peak frontier", "Time (µs)"]
    md.append(md_table(hdr, [[r[0], r[4], r[5], r[6], r[7], r[8], r[9], r[11]] for r in main_rows]))
    md += ["\n## Summary by category\n", md_table(summ_header, summ_rows),
           "\n## Branch and Bound with transfer penalty\n",
           md_table(["ID", "Penalty km", "Hops", "km", "Transfers", "Visited states", "Time (µs)"],
                    [[r[0], r[2], r[3], r[4], r[5], r[6], r[8]] for r in pen_rows]),
           "\n## DFS neighbour-order sensitivity (50 random orders)\n",
           md_table(["ID", "min hops", "mean hops", "max hops", "sd", "min km", "mean km",
                     "max km", "BFS hops", "optimal km"], [r[:1] + r[2:] for r in sens_rows]),
           "\n## Routes found\n",
           md_table(["ID", "Alg", "Route"], [[r[0], r[4], r[14]] for r in main_rows])]
    with open(os.path.join(RESULTS, "results_tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    make_figures(g, detail)
    print("Done. Results in", RESULTS)


def make_figures(g, detail):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - figures skipped")
        return
    # Figure 1: the weighted graph drawn on its coordinates
    colours = {"K1": "#1f77b4", "K2": "#ff7f0e", "K3": "#c49c6b", "K4": "#8cbf3f",
               "K5": "#9b8fc8", "F7": "#8c2d3a", "F8": "#5b3f8c", "F9": "#3bb3b3",
               "F10": "#e8a33d", "F12": "#d62728", "KRL": "#e31a1c", "BIAS": "#1aa86a",
               "BK": "#a50f15", "WALK": "#222222"}
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=200)
    drawn = set()
    for (u, v), cs in g.corridors.items():
        for c in set(cs):
            if (v, u, c) in drawn:
                continue
            drawn.add((u, v, c))
            rail = c in ("KRL", "BIAS", "BK")
            ax.plot([g.lon[u], g.lon[v]], [g.lat[u], g.lat[v]], color=colours[c],
                    lw=1.8 if rail else 1.1, ls="--" if rail or c == "WALK" else "-", zorder=1,
                    label=c if c not in [l.get_label() for l in ax.lines] else None)
    hubs = ["Terminal Kartasura", "Terminal Palur", "Terminal Tirtonadi", "Bandara Adi Soemarmo",
            "Solo Balapan", "Purwosari", "Solo Jebres", "Solo Kota", "Gladag", "Pasar Klewer",
            "Panggung", "Lapangan Gentan", "Simpang Sidan", "Sub Terminal Pelangi Mojosongo",
            "Sub Terminal Semanggi", "Stadion Manahan", "RSUD Ngipang", "Kadipiro"]
    xs = [g.lon[i] for i in g.name]
    ys = [g.lat[i] for i in g.name]
    ax.scatter(xs, ys, s=4, c="black", zorder=2)
    for h in hubs:
        i = g.id(h)
        ax.scatter([g.lon[i]], [g.lat[i]], s=22, c="white", edgecolors="black", zorder=3)
        ax.annotate(h, (g.lon[i], g.lat[i]), fontsize=5.5, xytext=(3, 3),
                    textcoords="offset points", zorder=4)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°)")
    ax.set_title(f"Weighted Surakarta transit graph (|V| = {g.n_nodes}, |E| = {g.n_edges})", fontsize=9)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=6, ncol=2, loc="lower left", frameon=True)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig1_network.png"))
    plt.close(fig)

    # Figure 2: distance per route
    ids = [r[0] for r in ROUTES]
    algs = ["BFS", "DFS", "B&B"]
    cols = {"BFS": "#4c72b0", "DFS": "#c44e52", "B&B": "#55a868"}
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), dpi=200)
    width = 0.27
    for k, a in enumerate(algs):
        axes[0].bar([i + (k - 1) * width for i in range(len(ids))],
                    [detail[(r, a)]["km"] for r in ids], width, label=a, color=cols[a])
        axes[1].bar([i + (k - 1) * width for i in range(len(ids))],
                    [detail[(r, a)]["visited"] for r in ids], width, label=a, color=cols[a])
    for ax_, yl, tt in ((axes[0], "Total distance (km)", "(a) Route distance"),
                        (axes[1], "Visited nodes", "(b) Nodes expanded")):
        ax_.set_xticks(range(len(ids)))
        ax_.set_xticklabels(ids, fontsize=7)
        ax_.set_ylabel(yl, fontsize=8)
        ax_.set_title(tt, fontsize=9)
        ax_.grid(axis="y", alpha=0.3)
        ax_.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig2_distance_visited.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
