"""
paper_figures.py
----------------
Draws the figures used in the paper from the CSV files in results/ (no
re-timing, so the figures always match the tables).

    python src/paper_figures.py
"""
import csv
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transit_graph import TransitGraph  # noqa: E402

ROOT = os.path.dirname(HERE)
RES, FIG = os.path.join(ROOT, "results"), os.path.join(ROOT, "figures")
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "FreeSerif", "DejaVu Serif"],
                     "font.size": 8})

COLOURS = {"K1": "#1f77b4", "K2": "#ff7f0e", "K3": "#b08850", "K4": "#7fb03a", "K5": "#9b8fc8",
           "F7": "#8c2d3a", "F8": "#5b3f8c", "F9": "#2aa7a7", "F10": "#e8a33d", "F12": "#d62728",
           "KRL": "#e31a1c", "BIAS": "#1aa86a", "BK": "#a50f15", "WALK": "#222222"}
ALG_COL = {"BFS": "#4c72b0", "DFS": "#c44e52", "B&B": "#55a868"}


# Labels drawn on the full map (offset in points) and in the city-centre inset.
LABELS_MAIN = {   # name: (dx, dy, horizontal alignment) in points
    "Bandara Adi Soemarmo": (5, 3, "left"), "Terminal Kartasura": (-2, 8, "left"),
    "Kadipiro": (5, 2, "left"), "RSUD Ngipang": (5, 3, "left"),
    "Sub Terminal Pelangi Mojosongo": (5, 2, "left"), "Goa Maria": (5, 0, "left"),
    "Purwosari": (-4, 7, "right"), "Kleco": (0, -9, "center"), "Taman Lansia": (4, 5, "left"),
    "Terminal Palur": (3, 7, "left"), "UNS": (0, -9, "center"), "Lapangan Gentan": (5, -2, "left"),
    "Sub Terminal Semanggi": (5, -6, "left"), "Simpang Sidan": (-3, 7, "right"),
    "Pasar Bekonang": (-3, -8, "right"), "Graha Saba Buana": (-4, 4, "right"),
}
LABELS_INSET = {
    "Terminal Tirtonadi": (-4, 6, "right"), "Stadion Manahan": (3, 7, "left"),
    "Solo Balapan": (5, 3, "left"), "Panggung": (-3, 8, "right"), "Solo Jebres": (0, -9, "center"),
    "Pasar Legi": (-4, -3, "right"), "Pasar Gede": (5, 0, "left"), "Gladag": (-2, 7, "right"),
    "Benteng Vastenburg": (6, -5, "left"), "Pasar Klewer": (-4, -6, "right"),
    "Solo Kota": (0, -9, "center"), "Gendengan": (3, -8, "left"), "Pasar Pon": (-4, 5, "right"),
    "Gemblegan": (-4, -7, "right"), "Pasar Gading": (4, -7, "left"),
}
INSET_BOX = (110.802, 110.842, -7.586, -7.550)     # lon_min, lon_max, lat_min, lat_max

CORRIDOR_ORDER = ["K1", "K2", "K3", "K4", "K5", "F7", "F8", "F9", "F10", "F12",
                  "KRL", "BIAS", "BK", "WALK"]
RAIL = ("KRL", "BIAS", "BK", "WALK")


def _draw_corridors(ax, g, gap_deg, lw_bus, lw_rail):
    """Draw every corridor; corridors that share a segment are drawn side by
    side (offset perpendicular to the segment) so none is hidden."""
    pairs = {}
    for (u, v), cs in g.corridors.items():
        key = (min(u, v), max(u, v))
        pairs.setdefault(key, set()).update(cs)
    for (u, v), cs in pairs.items():
        cs = [c for c in CORRIDOR_ORDER if c in cs]
        x1, y1, x2, y2 = g.lon[u], g.lat[u], g.lon[v], g.lat[v]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1.0
        px, py = -dy / n, dx / n
        for i, c in enumerate(cs):
            off = (i - (len(cs) - 1) / 2) * gap_deg
            rail = c in RAIL
            ax.plot([x1 + px * off, x2 + px * off], [y1 + py * off, y2 + py * off],
                    color=COLOURS[c], lw=lw_rail if rail else lw_bus,
                    ls=(0, (3, 1.5)) if rail else "-", solid_capstyle="round", zorder=2 if rail else 1)


def _draw_stops(ax, g, s_stop, s_hub):
    multi = {i for i in g.name if len({c for (a, b), cs in g.corridors.items() if a == i for c in cs}) > 1}
    ax.scatter([g.lon[i] for i in g.name if i not in multi], [g.lat[i] for i in g.name if i not in multi],
               s=s_stop, c="black", lw=0, zorder=3)
    ax.scatter([g.lon[i] for i in multi], [g.lat[i] for i in multi], s=s_hub, c="white",
               edgecolors="black", lw=0.5, zorder=4)


def _label(ax, g, name, off, size):
    i = g.id(name)
    dx, dy, ha = off
    t = ax.annotate(name, (g.lon[i], g.lat[i]), xytext=(dx, dy), textcoords="offset points",
                    fontsize=size, zorder=6, ha=ha, va="center", annotation_clip=True)
    t.set_clip_on(True)
    t.set_path_effects([pe.withStroke(linewidth=1.8, foreground="white")])


def fig_network(g):
    lat0 = sum(g.lat.values()) / len(g.lat)
    aspect = 1 / math.cos(math.radians(lat0))
    fig = plt.figure(figsize=(7.0, 3.4), dpi=300)
    ax = fig.add_axes([0.07, 0.11, 0.55, 0.78])
    ins = fig.add_axes([0.675, 0.11, 0.315, 0.78])

    # (a) whole network
    _draw_corridors(ax, g, gap_deg=0.00042, lw_bus=0.7, lw_rail=0.95)
    _draw_stops(ax, g, s_stop=1.0, s_hub=3.5)
    for name, off in LABELS_MAIN.items():
        _label(ax, g, name, off, 5.2)
    xmin, xmax = min(g.lon.values()), max(g.lon.values())
    ymin, ymax = min(g.lat.values()), max(g.lat.values())
    ax.set_xlim(xmin - 0.006, xmax + 0.006)
    ax.set_ylim(ymin - 0.005, ymax + 0.005)
    ax.set_aspect(aspect, adjustable="datalim")
    ax.set_xlabel("Longitude (°E)", fontsize=7)
    ax.set_ylabel("Latitude (°)", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(alpha=0.2, lw=0.3)
    ax.set_title("(a) Whole network", fontsize=7, pad=3)
    km_deg = 2 / (111.320 * math.cos(math.radians(lat0)))
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    sx, sy = x0 + 0.04 * (x1 - x0), y0 + 0.06 * (y1 - y0)
    ax.plot([sx, sx + km_deg], [sy, sy], color="black", lw=1.2, zorder=7)
    ax.text(sx + km_deg / 2, sy + 0.025 * (y1 - y0), "2 km", ha="center", fontsize=5.5, zorder=7)
    bx = INSET_BOX
    ax.add_patch(plt.Rectangle((bx[0], bx[2]), bx[1] - bx[0], bx[3] - bx[2], fill=False,
                               ec="0.3", lw=0.6, ls="--", zorder=8))
    ax.text(bx[1] + 0.0008, bx[2], "(b)", fontsize=6, color="0.3", zorder=8, va="bottom")

    # (b) city centre
    _draw_corridors(ins, g, gap_deg=0.00012, lw_bus=0.85, lw_rail=1.05)
    _draw_stops(ins, g, s_stop=1.8, s_hub=6)
    for name, off in LABELS_INSET.items():
        _label(ins, g, name, off, 5.0)
    ins.set_xlim(bx[0], bx[1])
    ins.set_ylim(bx[2], bx[3])
    ins.set_aspect(aspect, adjustable="datalim")
    ins.tick_params(labelsize=5.5)
    from matplotlib.ticker import FormatStrFormatter, MaxNLocator
    for a_ in (ax, ins):
        a_.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        a_.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ins.xaxis.set_major_locator(MaxNLocator(4))
    ins.yaxis.set_major_locator(MaxNLocator(5))
    ins.grid(alpha=0.2, lw=0.3)
    ins.set_title("(b) City centre", fontsize=7, pad=3)
    km1 = 1 / (111.320 * math.cos(math.radians(lat0)))
    ix0, ix1 = ins.get_xlim()
    iy0, iy1 = ins.get_ylim()
    sx, sy = ix0 + 0.70 * (ix1 - ix0), iy0 + 0.05 * (iy1 - iy0)
    ins.plot([sx, sx + km1], [sy, sy], color="black", lw=1.2, zorder=7)
    ins.text(sx + km1 / 2, sy + 0.025 * (iy1 - iy0), "1 km", ha="center", fontsize=5.5, zorder=7)

    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color=COLOURS[c], lw=1.4, ls=(0, (3, 1.5)) if c in RAIL else "-",
                      label=c) for c in CORRIDOR_ORDER]
    handles += [Line2D([0], [0], marker="o", ls="", mfc="white", mec="black", ms=3.5, mew=0.6,
                       label="interchange"),
                Line2D([0], [0], marker="o", ls="", mfc="black", mec="black", ms=1.8, label="stop")]
    fig.legend(handles=handles, fontsize=5.4, ncol=16, loc="upper center", bbox_to_anchor=(0.5, 0.995),
               frameon=False, handlelength=1.8, columnspacing=0.8, handletextpad=0.4)
    fig.savefig(os.path.join(FIG, "paper_fig1_network.png"))
    plt.close(fig)


def fig_results():
    rows = list(csv.DictReader(open(os.path.join(RES, "results_main.csv"), encoding="utf-8")))
    d = {(r["route_id"], r["algorithm"]): r for r in rows}
    ids = [r["route_id"] for r in rows if r["algorithm"] == "BFS"]
    fig, axes = plt.subplots(2, 1, figsize=(3.35, 4.1), dpi=300)
    w = 0.27
    for k, a in enumerate(("BFS", "DFS", "B&B")):
        xs = [i + (k - 1) * w for i in range(len(ids))]
        axes[0].bar(xs, [float(d[(r, a)]["distance_km"]) for r in ids], w, label=a, color=ALG_COL[a])
        axes[1].bar(xs, [int(d[(r, a)]["visited_nodes"]) for r in ids], w, label=a, color=ALG_COL[a])
    for ax, yl, t in ((axes[0], "Distance (km)", "(a) Total route distance"),
                      (axes[1], "Visited nodes", "(b) Nodes expanded during search")):
        ax.set_xticks(range(len(ids)))
        ax.set_xticklabels(ids, fontsize=6)
        ax.set_ylabel(yl)
        ax.set_title(t, fontsize=8)
        ax.grid(axis="y", alpha=0.3, lw=0.4)
        ax.legend(fontsize=6, loc="upper left", ncol=3)
    axes[0].set_ylim(0, 85)
    axes[1].set_ylim(0, 380)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "paper_fig2_distance_visited.png"))
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    graph = TransitGraph.from_csv(os.path.join(ROOT, "data", "nodes.csv"),
                                  os.path.join(ROOT, "data", "edges.csv"))
    fig_network(graph)
    fig_results()
    print("Figures written to", FIG)
