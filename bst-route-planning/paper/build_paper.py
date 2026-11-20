# -*- coding: utf-8 -*-
"""
build_paper.py
--------------
Rebuilds the ITSmart paper (.docx) from the group's template and the CSV files
in results/, so the tables always match the latest benchmark run.

    python paper/build_paper.py

The prose (Sections 1-5) quotes specific numbers; if you re-run the benchmark
on another machine, the tables update automatically but the timing figures
quoted in the text must be updated by hand.
"""
import csv
import os
import re
import shutil
import statistics
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TEMPLATE_DOCX = os.path.join(HERE, "itsmart_template.docx")   # group template (runs merged)
OUT_DIR = os.path.join(HERE, "_build")
OUT_DOCX = os.path.join(HERE, "Paper_BFS_DFS_BnB_Surakarta_ITSmart.docx")

COL_W = 4802      # one column, dxa
FULL_W = 10080    # page text width, dxa

# ------------------------------------------------------------------ helpers
def runs(text, base_rpr="", size=None):
    """*italic*, _{sub}, ^{sup}, {cite:key} handled; returns w:r xml."""
    out = []
    pat = re.compile(r"(\*[^*]+\*|_\{[^}]+\}|\^\{[^}]+\})")
    for tok in pat.split(text):
        if not tok:
            continue
        rpr = base_rpr
        if tok.startswith("*") and tok.endswith("*"):
            tok, rpr = tok[1:-1], rpr + "<w:i/><w:iCs/>"
        elif tok.startswith("_{"):
            tok, rpr = tok[2:-1], rpr + '<w:vertAlign w:val="subscript"/>'
        elif tok.startswith("^{"):
            tok, rpr = tok[2:-1], rpr + '<w:vertAlign w:val="superscript"/>'
        if size:
            rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        out.append(f'<w:r>{"<w:rPr>"+rpr+"</w:rPr>" if rpr else ""}'
                   f'<w:t xml:space="preserve">{escape(tok)}</w:t></w:r>')
    return "".join(out)


CITE_ORDER = []


def cite(text):
    def rep(m):
        keys = [k.strip() for k in m.group(1).split(",")]
        nums = []
        for k in keys:
            if k not in CITE_ORDER:
                CITE_ORDER.append(k)
            nums.append(CITE_ORDER.index(k) + 1)
        return ", ".join(f"[{n}]" for n in nums)
    return re.sub(r"\{cite:([^}]+)\}", rep, text)


def para(text, first=True):
    ind = '' if first else ''
    return (f'<w:p><w:pPr><w:pStyle w:val="BodyTextIndent"/>{ind}</w:pPr>'
            f'{runs(cite(text))}</w:p>')


def para_noindent(text, after=0):
    return (f'<w:p><w:pPr><w:pStyle w:val="BodyTextIndent"/><w:spacing w:after="{after}"/>'
            f'<w:ind w:firstLine="0"/></w:pPr>{runs(cite(text))}</w:p>')


def h1(text):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:numPr><w:ilvl w:val="0"/>'
            f'<w:numId w:val="1"/></w:numPr><w:spacing w:before="160"/></w:pPr>{runs(text)}</w:p>')


def h2(text):
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading2"/><w:keepLines w:val="0"/><w:numPr>'
            f'<w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr><w:spacing w:before="80" w:after="0"/>'
            f'<w:jc w:val="left"/></w:pPr>{runs(text)}</w:p>')


def caption(kind, n, text, before=60):
    return (f'<w:p><w:pPr><w:pStyle w:val="Caption"/><w:keepNext/><w:spacing w:before="{before}" w:after="60"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{kind} {n}. </w:t></w:r>{runs(text)}</w:p>')


def caption_below(kind, n, text):
    return (f'<w:p><w:pPr><w:pStyle w:val="Caption"/><w:spacing w:before="40" w:after="120"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{kind} {n}. </w:t></w:r>{runs(text)}</w:p>')


def bullet(text):
    return (f'<w:p><w:pPr><w:pStyle w:val="BodyTextIndent"/><w:ind w:left="284" w:hanging="200"/>'
            f'</w:pPr>{runs("• " + cite(text))}</w:p>')


def table(header, rows, widths, size=15, header_rows=None, bold_cols=None, align=None):
    """Simple grid table in the template's style. header_rows: list of rows for
    multi-row headers given as [(text, span), ...]."""
    borders = ''.join(f'<w:{b} w:val="single" w:sz="2" w:space="0" w:color="000000"/>'
                      for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    total = sum(widths)
    x = [f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:jc w:val="center"/>'
         f'<w:tblBorders>{borders}</w:tblBorders><w:tblLayout w:type="fixed"/>'
         f'<w:tblCellMar><w:left w:w="40" w:type="dxa"/><w:right w:w="40" w:type="dxa"/></w:tblCellMar>'
         f'</w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>']

    def cell(text, w, bold=False, span=1, jc="center"):
        rpr = "<w:b/><w:bCs/>" if bold else ""
        gs = f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{gs}<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:pStyle w:val="BodyTextIndent"/><w:ind w:firstLine="0"/>'
                f'<w:jc w:val="{jc}"/></w:pPr>{runs(text, rpr, size)}</w:p></w:tc>')
    for hr in (header_rows or []):
        x.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>')
        i = 0
        for text, span in hr:
            x.append(cell(text, sum(widths[i:i + span]), True, span))
            i += span
        x.append('</w:tr>')
    if header:
        x.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>' +
                 ''.join(cell(h, w, True) for h, w in zip(header, widths)) + '</w:tr>')
    for r in rows:
        x.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>')
        for j, (c, w) in enumerate(zip(r, widths)):
            jc = (align[j] if align else "center")
            x.append(cell(str(c), w, bold=bool(bold_cols and j in bold_cols), jc=jc))
        x.append('</w:tr>')
    x.append('</w:tbl>')
    return ''.join(x)


def spacer(after=60):
    return f'<w:p><w:pPr><w:spacing w:before="0" w:after="{after}"/></w:pPr></w:p>'


SECT_2COL = ('<w:sectPr><w:type w:val="continuous"/><w:pgSz w:w="12240" w:h="15840" w:code="1"/>'
             '<w:pgMar w:top="1440" w:right="1080" w:bottom="1440" w:left="1080" w:header="720" '
             'w:footer="720" w:gutter="0"/><w:cols w:num="2" w:space="475"/></w:sectPr>')
SECT_1COL = SECT_2COL.replace('<w:cols w:num="2" w:space="475"/>', '<w:cols w:space="720"/>')


def end_section(two_col):
    return (f'<w:p><w:pPr><w:spacing w:before="0" w:after="0"/>'
            f'{SECT_2COL if two_col else SECT_1COL}</w:pPr></w:p>')


IMG_ID = [100]


def image(rid, w_in, h_in, name):
    IMG_ID[0] += 1
    cx, cy = int(w_in * 914400), int(h_in * 914400)
    n = IMG_ID[0]
    return (f'<w:p><w:pPr><w:pStyle w:val="BodyTextIndent"/><w:keepNext/><w:spacing w:before="60" w:after="0"/>'
            f'<w:ind w:firstLine="0"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{n}" name="{name}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{n}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData>'
            f'</a:graphic></wp:inline></w:drawing></w:r></w:p>')


# ---- Office Math helpers
def mr(t, plain=False):
    sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if plain else ''
    return f'<m:r>{sty}<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">{escape(t)}</m:t></m:r>'


def msub(base, sub):
    return f'<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>'


def msup(base, sup):
    return f'<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>'


def mfrac(num, den):
    return f'<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'


def mrad(e):
    return f'<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>{e}</m:e></m:rad>'


def mparen(e):
    return f'<m:d><m:e>{e}</m:e></m:d>'


def mfunc(name, arg):
    return f'<m:func><m:fName>{mr(name, True)}</m:fName><m:e>{arg}</m:e></m:func>'


def msum(lo, hi, e):
    return (f'<m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr>'
            f'<m:sub>{lo}</m:sub><m:sup>{hi}</m:sup><m:e>{e}</m:e></m:nary>')


def equation(omml, num):
    return (f'<w:p><w:pPr><w:pStyle w:val="BodyTextIndent"/><w:tabs><w:tab w:val="center" w:pos="2400"/>'
            f'<w:tab w:val="right" w:pos="4790"/></w:tabs><w:spacing w:before="60" w:after="60"/>'
            f'<w:ind w:firstLine="0"/></w:pPr><w:r><w:tab/></w:r><m:oMath>{omml}</m:oMath>'
            f'<w:r><w:tab/><w:t>({num})</w:t></w:r></w:p>')


def pseudocode(title, lines):
    rows = []
    rows.append(f'<w:p><w:pPr><w:spacing w:before="0" w:after="20"/><w:jc w:val="left"/></w:pPr>'
                f'{runs(title, "<w:b/>", 16)}</w:p>')
    for ln in lines:
        rows.append(f'<w:p><w:pPr><w:spacing w:before="0" w:after="0"/><w:jc w:val="left"/></w:pPr>'
                    f'<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
                    f'<w:sz w:val="14"/><w:szCs w:val="14"/></w:rPr><w:t xml:space="preserve">{escape(ln)}</w:t></w:r></w:p>')
    borders = ''.join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                      for b in ("top", "left", "bottom", "right"))
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{COL_W}" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
            f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
            f'<w:bottom w:w="40" w:type="dxa"/><w:right w:w="60" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{COL_W}"/></w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr><w:tc><w:tcPr>'
            f'<w:tcW w:w="{COL_W}" w:type="dxa"/></w:tcPr>{"".join(rows)}</w:tc></w:tr></w:tbl>')


# ------------------------------------------------------------------ data
def load(name):
    with open(os.path.join(PROJ, "results", name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


MAIN = load("results_main.csv")
D = {(r["route_id"], r["algorithm"]): r for r in MAIN}
SCEN = load("route_scenarios.csv")
SUMM = load("summary_by_category.csv")
PEN = load("bnb_transfer_penalty.csv")
IDS = [r["route_id"] for r in SCEN]

import struct
with open(os.path.join(PROJ, "figures", "paper_fig1_network.png"), "rb") as _f:
    _hdr = _f.read(24)
FIG1_W, FIG1_H = struct.unpack(">II", _hdr[16:24])

# ================================================================== STATISTICS
# Every number quoted in the prose is computed here from the CSV files, so the
# text, the tables and the figures always agree.
NODES = list(csv.DictReader(open(os.path.join(PROJ, "data", "nodes.csv"), encoding="utf-8")))
EDGES = list(csv.DictReader(open(os.path.join(PROJ, "data", "edges.csv"), encoding="utf-8")))
ALGS = ("BFS", "DFS", "B&B")
RAIL_C = ("KRL", "BIAS", "BK")
PRETTY = {"KRL": "the KRL", "BIAS": "the airport railway", "BK": "the Batara Kresna railbus",
          "WALK": "the skybridge"}


def C(keys):
    return "{cite:" + keys + "}"


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def legs(route):
    return [seg.split(":")[0].strip() for seg in route.split("|")]


def corridor_list(route):
    names = []
    for seg in route.split("|"):
        c = seg.split(":")[0].strip()
        if c == "WALK":
            names.append("the Tirtonadi skybridge" if "Tirtonadi" in seg else "a short interchange walk")
        else:
            names.append(PRETTY.get(c, c))
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def join_ids(ids):
    ids = list(ids)
    if not ids:
        return "none"
    if len(ids) == 1:
        return ids[0]
    return ", ".join(ids[:-1]) + " and " + ids[-1]


def n_tr(n):
    return "no transfers" if n == 0 else ("one transfer" if n == 1 else f"{n} transfers")


def times_word(n):
    return {1: "once", 2: "twice"}.get(n, f"{num_word(n)} times")


def num_word(n):
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
             "eleven", "twelve", "thirteen", "fourteen", "fifteen"]
    return words[n] if n < len(words) else str(n)


SUM = {(r["category"], r["algorithm"]): r for r in SUMM}


def sm(alg, key, cat="All"):
    return float(SUM[(cat, alg)][key])


ROUTE_NAME = {r["route_id"]: f'{r["origin"]} to {r["destination"]}' for r in SCEN}
km = {(i, a): float(D[(i, a)]["distance_km"]) for i in IDS for a in ALGS + ("Dijkstra",)}
hops = {(i, a): int(D[(i, a)]["hops"]) for i in IDS for a in ALGS}
trf = {(i, a): int(D[(i, a)]["transfers"]) for i in IDS for a in ALGS}
gap = {i: (km[(i, "BFS")] / km[(i, "B&B")] - 1) * 100 for i in IDS}
worst = max(IDS, key=lambda i: gap[i])
bfs_opt = [i for i in IDS if abs(km[(i, "BFS")] - km[(i, "B&B")]) < 1e-9]
bfs_rail = [i for i in IDS if any(c in RAIL_C for c in legs(D[(i, "BFS")]["route"]))]
bnb_rail = [i for i in IDS if any(c in RAIL_C for c in legs(D[(i, "B&B")]["route"]))]
bfs_more_tr = [i for i in IDS if trf[(i, "BFS")] > trf[(i, "B&B")]]
bfs_less_tr = [i for i in IDS if trf[(i, "BFS")] < trf[(i, "B&B")]]
dfs_worst = max(IDS, key=lambda i: km[(i, "DFS")])
all_bnb_eq_dij = all(abs(km[(i, "B&B")] - km[(i, "Dijkstra")]) < 1e-9 for i in IDS)
assert all_bnb_eq_dij
# example 1: route where BFS is longest relative to B&B while B&B has fewer transfers
ex1 = max(IDS, key=lambda i: (trf[(i, "BFS")] - trf[(i, "B&B")], gap[i]))
# example 2: a route where BFS needs fewer transfers than B&B (if any)
ex2 = bfs_less_tr[0] if bfs_less_tr else None
rail_means = {c: statistics.mean(float(e["distance_km"]) for e in EDGES if e["corridor"] == c)
              for c in RAIL_C}
bus_edges = [float(e["distance_km"]) for e in EDGES if e["mode"] == "bus"]
_src = {n["stop_name"]: n["coord_source"] for n in NODES}
min_edge = min((e for e in EDGES if _src[e["from_stop"]] == "osm" and _src[e["to_stop"]] == "osm"),
               key=lambda e: float(e["distance_km"]))
max_edge = max(EDGES, key=lambda e: float(e["distance_km"]))
n_multi = sum(1 for n in NODES if len(n["corridors"].split("|")) > 1)
src_counts = {}
for n in NODES:
    src_counts[n["coord_source"]] = src_counts.get(n["coord_source"], 0) + 1
n_osm = src_counts.get("osm", 0)
n_interp = src_counts.get("interpolated", 0)
n_manual = src_counts.get("manual", 0)
SENS = load("dfs_order_sensitivity.csv")
sens_mean_hops = statistics.mean(float(x["dfs_mean_hops"]) for x in SENS)
sens_mean_km = statistics.mean(float(x["dfs_mean_km"]) for x in SENS)
sens_max_hops = max(int(x["dfs_max_hops"]) for x in SENS)
sens_best_opt = sum(1 for x in SENS if abs(float(x["dfs_min_km"]) - float(x["optimal_km"])) < 0.005)
max_peak = {a: max(int(D[(i, a)]["peak_frontier"]) for i in IDS) for a in ALGS + ("Dijkstra",)}
vis_red = (1 - sm("B&B", "mean_visited") / sm("Dijkstra", "mean_visited")) * 100
ENV = open(os.path.join(PROJ, "results", "environment.txt"), encoding="utf-8").read()
PY_VER = re.search(r"Python (\S+)", ENV).group(1)
CPU = re.search(r"CPU: (.*?);", ENV).group(1)
REPS = re.search(r"median of (\d+) runs", ENV).group(1)

# penalty experiment
PENS = ("0", "1", "2.5", "5")
pen_tot = {}
for pen in PENS:
    rr = [x for x in PEN if x["penalty_km_per_transfer"] == pen]
    pen_tot[pen] = dict(km=sum(float(x["distance_km"]) for x in rr),
                        tr=sum(int(x["transfers"]) for x in rr),
                        hops=sum(int(x["hops"]) for x in rr),
                        vis=statistics.mean(int(x["visited_states"]) for x in rr),
                        t=statistics.mean(float(x["time_us_median"]) for x in rr),
                        rows={x["route_id"]: x for x in rr})
pen_changed = {pen: [i for i in IDS if int(pen_tot[pen]["rows"][i]["transfers"]) <
                     int(pen_tot["0"]["rows"][i]["transfers"])] for pen in PENS}
pen1_inc = (pen_tot["1"]["km"] / pen_tot["0"]["km"] - 1) * 100
pen_last = PENS[-1]
pen_last_inc = (pen_tot[pen_last]["km"] / pen_tot["0"]["km"] - 1) * 100
first_full = next(p for p in PENS[1:] if pen_tot[p]["tr"] == pen_tot[pen_last]["tr"])
ex3 = max(pen_changed["1"], key=lambda i: int(pen_tot["0"]["rows"][i]["transfers"]) -
          int(pen_tot["1"]["rows"][i]["transfers"])) if pen_changed["1"] else None
vis_ratio = [pen_tot[p]["vis"] / pen_tot["0"]["vis"] for p in PENS[1:]]
t_ratio = [pen_tot[p]["t"] / pen_tot["0"]["t"] for p in PENS[1:]]

# ================================================================== CONTENT
TITLE = ("Comparative Analysis of Breadth-First Search, Depth-First Search, and Branch-and-Bound "
         "Algorithms for Weighted Multi-Corridor Public Transit Route Planning in Surakarta")

ABSTRACT = (
    "Surakarta's integrated public transport network combines five Batik Solo Trans (BST) corridors, "
    f"five feeder routes and three rail services, with inter-stop spacing from under 0.1 km between "
    f"neighbouring kerbside stops to over {int(float(max_edge['distance_km']))} km on rail links, so a "
    "planner that counts only stops can "
    "return routes that are short in hops but long in kilometres. This study models the October 2026 "
    f"Surakarta integration map as a weighted graph G = (V, E, W) of {len(NODES)} stops and {len(EDGES)} "
    "corridor edges, with stop coordinates geocoded from OpenStreetMap and each edge weighted by its "
    "Haversine distance multiplied by a circuity factor (1.2 road, 1.1 rail). Breadth-First Search (BFS), "
    "Depth-First Search (DFS) and least-cost Branch-and-Bound (B&B) with a straight-line lower bound were "
    "implemented in Python and evaluated on 15 short, medium and long origin-destination scenarios. B&B "
    "returned the minimum-distance route in every scenario, as verified against Dijkstra's algorithm, "
    f"averaging {f2(sm('B&B', 'mean_km'))} km and {f1(sm('B&B', 'mean_transfers'))} transfers. BFS minimised "
    f"stops ({f1(sm('BFS', 'mean_hops'))} on average), but its routes were "
    f"{f1(sm('BFS', 'mean_km_gap_vs_optimal_pct'))}% longer on average (up to {f1(gap[worst])}%) because "
    f"hop counting favours long rail edges, and needed {f1(sm('BFS', 'mean_transfers'))} transfers. DFS "
    f"routes averaged {f2(sm('DFS', 'mean_km'))} km and {f1(sm('DFS', 'mean_hops'))} stops. BFS was fastest "
    f"at {f1(sm('BFS', 'mean_time_us'))} µs per query; B&B expanded {f1(vis_red)}% fewer nodes than "
    f"Dijkstra but took {f1(sm('B&B', 'mean_time_us'))} µs because evaluating the bound is costly at this "
    f"graph size. A 1 km transfer penalty cut total transfers from {pen_tot['0']['tr']} to "
    f"{pen_tot['1']['tr']} for {f1(pen1_inc)}% more distance. Distance-weighted B&B is therefore "
    "recommended for journey planning, and BFS for fast hop-count queries.")

KEYWORDS = ("Batik Solo Trans, branch and bound, breadth-first search, depth-first search, "
            "weighted graph")

body = []
add = body.append

# ---------------------------------------------------------------- 1
add(h1("INTRODUCTION"))
add(para(
    "Surakarta (Solo) operates a multi-layered urban public transport system. The October 2026 edition "
    "of the official integration map, *Peta Integrasi Transportasi Umum Surakarta dan Sekitarnya*, "
    "published by the Surakarta Transport Agency (Dinas Perhubungan) with the Transport for Solo "
    "community, shows five Batik Solo Trans (BST) bus corridors (K1 Terminal Palur–Bandara Adi "
    "Soemarmo, K2 Terminal Palur–Purwosari, K3 Terminal Kartasura–Taman Lansia, K4 Terminal "
    "Kartasura–Terminal Palur and K5 Terminal Kartasura–Simpang Sidan), five feeder microbus routes "
    "(F7, F8, F9, F10 and F12), two Trans Jateng regional routes and three rail services that stop in "
    "the city: the KRL commuter line Yogyakarta–Palur, the Adi Soemarmo airport railway and the Batara "
    "Kresna railbus. Previous work on the BST network has measured its spatial coverage, showing that a "
    f"400 m service area around existing stops reaches 126 elementary schools and 43 urban villages "
    f"{C('syaharini')}, but has not examined how passengers find a route through the network once they "
    "are on it."))
add(para(
    "Route finding is naturally a graph problem. In the widely used L-space representation, every stop is "
    f"a vertex and two consecutive stops of a corridor are joined by an edge {C('xiao')}. Breadth-First "
    "Search (BFS) on such a graph returns the route with the fewest stops, and journey planners commonly "
    f"treat the number of transfers as an objective in its own right {C('baum, srikanth')}. Stop "
    "spacing, however, is far from uniform. In the dataset built for this study, edges range from "
    f"{f2(float(min_edge['distance_km']))} km between {min_edge['from_stop']} and {min_edge['to_stop']} to "
    f"{f2(float(max_edge['distance_km']))} km between {max_edge['from_stop']} and {max_edge['to_stop']} on "
    f"{PRETTY.get(max_edge['corridor'], max_edge['corridor'])}. One hop can therefore mean a short ride "
    "between neighbouring stops or a long train journey, and a route that is minimal in hops is not "
    "necessarily minimal in kilometres travelled."))
add(para(
    f"Indonesian studies have compared BFS and Depth-First Search (DFS) for waste collection trucks "
    f"{C('bernov')}, tourist itineraries {C('darip')} and courier distribution {C('prasetyo')}, applied "
    f"an improved BFS to public transit line search {C('kartoirono')} and used Dijkstra's algorithm for "
    f"tourist bus routes {C('mardiani')}. None of these studies compares unweighted traversal with a "
    "distance-guaranteeing weighted search on a multi-corridor network that mixes bus rapid transit, "
    "feeder and rail services, and none uses the current Surakarta network."))
add(para(
    "This study addresses that gap. Its objectives are to (i) abstract the 2026 Surakarta integration map "
    "into a reproducible weighted graph dataset with stop coordinates and edge distances in kilometres; "
    "(ii) implement BFS, DFS and a least-cost Branch-and-Bound (B&B) algorithm on that graph; (iii) "
    "compare them on 15 real origin-destination scenarios in terms of total distance, stops, transfers, "
    "visited nodes, peak memory footprint and execution time; and (iv) examine how a transfer penalty "
    "shifts the balance between distance and transfers. Section 2 reviews related work, Section 3 "
    "describes the dataset and algorithms, Section 4 presents and discusses the results, and Section 5 "
    "concludes."))

# ---------------------------------------------------------------- 2
add(h1("RELATED WORKS"))
add(para(
    f"Kartoirono *et al.* {C('kartoirono')} modelled the search for alternative bus lines as a graph "
    "problem and proposed an Improved BFS that keeps the level-by-level expansion of BFS but terminates "
    "early when a false finish point is detected; in their test from node 175 to node 54 the search time "
    "fell from 27 s 564 ms with standard BFS to 171 ms. Their work is the closest precedent for applying "
    "BFS to public transit, although it does not consider physical distance."))
add(para(
    f"Several Indonesian studies compare BFS and DFS directly. Bernov *et al.* {C('bernov')} built a "
    "route search system for waste carrier trucks in Sidoarjo Regency and found that BFS gave shorter "
    "routes, for example 9.3 km against 14.4 km with DFS from the depot to one collection node. Darip "
    f"*et al.* {C('darip')} simulated tourist routes to historical and cultural sites in Banten Province "
    "and reported that BFS tends to produce routes that are more efficient in distance, whereas DFS "
    f"explores more sites by going deep. Prasetyo *et al.* {C('prasetyo')} ran both algorithms on an "
    "unweighted road graph of Kaliuntu, Bali, with 15 nodes and 20 edges stored as an adjacency list; "
    "BFS was faster and more stable (0.082 ms against 0.158 ms) while DFS produced more distinct routes "
    "(9 against 6). These studies share the experimental design used here, namely adjacency lists, "
    "repeated timing and route-quality metrics, but their networks are small and none carries corridor "
    "or transfer information."))
add(para(
    f"On weighted route planning, Mardiani and Widayanti {C('mardiani')} applied Dijkstra's algorithm "
    "to plan a tourist transport route linking ten destinations in Surabaya, giving a route of 41.5 km. "
    f"Internationally, Lin and Hsieh {C('lin')} proposed a multicriteria search for route planning on "
    "existing mass-transit networks in Chicago and Tainan and benchmarked it against Dijkstra, BFS, "
    f"iterative-deepening DFS, best-first search and A∗ variants. Baum *et al.* {C('baum')} computed "
    "Pareto-optimal journeys by arrival time and number of trips with ULTRA, which precomputes transfer "
    f"shortcuts for algorithms such as RAPTOR, and Srikanth *et al.* {C('srikanth')} designed a "
    "temporal-paths-preservation graph and five algorithms that compute the minimum number of transfers "
    "in a public transportation network. These works establish that distance (or time) and transfers "
    "are distinct objectives, which motivates the transfer penalty examined in Section 4.3."))
add(para(
    f"Finally, Syaharini *et al.* {C('syaharini')} analysed the BST service area in Surakarta with GIS "
    f"network analysis and recommended 11 new stops, and Xiao *et al.* {C('xiao')} modelled the Xuzhou "
    "bus network in L-space to study its topology and robustness. Together, the literature shows that "
    "BFS and DFS have been compared mainly on small single-mode graphs, while weighted algorithms have "
    "been applied without a systematic comparison against unweighted traversal. No 2022–2026 study "
    "compares BFS, DFS and an optimal distance-based search on a multi-corridor BST, feeder and rail "
    "graph of Surakarta, which is the contribution of this paper."))

# ---------------------------------------------------------------- 3
add(h1("METHOD"))
add(h2("Weighted Graph Representation and Distance Calculation"))
add(para(
    "The network was digitised from the October 2026 integration map. The stop sequence of every corridor "
    "was transcribed in the order drawn on the map: the five BST corridors K1–K5, the feeder routes F7, "
    "F8, F9, F10 and F12, the Solo section of the KRL line (Purwosari–Solo Balapan–Solo Jebres–Palur), "
    "the airport railway (Bandara Adi Soemarmo–Kadipiro–Solo Balapan–Solo Jebres–Palur) and the Batara "
    "Kresna railbus (Purwosari–Solo Kota). The pedestrian skybridge between Terminal Tirtonadi and Solo "
    "Balapan station, which the map draws as a connection, was added as a walking edge. Where the map "
    "draws a bus stop and a station inside one interchange area, they were merged into a single vertex "
    "when they are at the same place (Solo Balapan, Palur, Bandara Adi Soemarmo) and joined by a short "
    "walking edge when they are a few hundred metres apart (Jebres and Solo Jebres station, Luwes "
    "Sangkrah and Solo Kota station), so that transfers connect correctly. Corridor K6 and feeder FD11 of "
    "earlier map editions no longer appear in the 2026 edition and were not modelled, and the Trans "
    "Jateng routes S1 and S2 were excluded because they mainly serve the neighbouring regencies."))
coord_txt = (f"Stop coordinates were obtained by geocoding every stop name with OpenStreetMap "
             f"(Nominatim) inside the Surakarta metropolitan area. A match was accepted only when it was a bus "
             f"stop, station or named landmark whose name agreed with the stop and its position was "
             f"consistent with the stop order of the corridor (checked automatically for back-tracking and "
             f"then by hand), which gave coordinates for {n_osm} stops")
if n_manual:
    coord_txt += f"; {n_manual} terminals and stations were placed manually from map references"
coord_txt += (f". The remaining {n_interp} stops, mostly small kerbside stops without a mapped "
              "landmark, were placed by linear interpolation between their geocoded neighbours along the "
              "corridor.")
add(para(
    f"The result is an undirected multigraph G = (V, E, W) with |V| = {len(NODES)} stops and "
    f"|E| = {len(EDGES)} corridor edges; {n_multi} stops are served by more than one corridor. Each vertex "
    "is stored in nodes.csv with its identifier, name, latitude, longitude, type, the corridors that serve "
    "it and the source of its coordinates, and each edge in edges.csv with its end stops, corridor, mode, "
    "straight-line distance, circuity factor and weight *w*(*u*, *v*) in km. " + coord_txt +
    " Figure 1 shows the resulting graph and Table 1 summarises it."))
per = {}
for e in EDGES:
    c = e["corridor"]
    p = per.setdefault(c, {"stops": set(), "n": 0, "km": 0.0, "max": 0.0})
    p["stops"] |= {e["from_id"], e["to_id"]}
    p["n"] += 1
    p["km"] += float(e["distance_km"])
    p["max"] = max(p["max"], float(e["distance_km"]))
order = ["K1", "K2", "K3", "K4", "K5", "F7", "F8", "F9", "F10", "F12", "KRL", "BIAS", "BK", "WALK"]
t1rows = [[c, len(per[c]["stops"]), per[c]["n"], f'{per[c]["km"]:.2f}',
           f'{per[c]["km"] / per[c]["n"]:.2f}', f'{per[c]["max"]:.2f}'] for c in order]
t1rows.append(["Total", len(NODES), len(EDGES), f'{sum(float(e["distance_km"]) for e in EDGES):.2f}',
               f'{statistics.mean(float(e["distance_km"]) for e in EDGES):.2f}',
               f'{max(float(e["distance_km"]) for e in EDGES):.2f}'])
add(caption("Table", 1, "Corridors in the weighted graph (BIAS = airport railway, BK = Batara Kresna)"))
add(table(["Corridor", "Stops", "Edges", "Length (km)", "Mean edge (km)", "Max edge (km)"], t1rows,
          [800, 700, 700, 900, 900, 800], size=15))
add(spacer(80))
add(para(
    "The straight-line distance between stops *u* and *v* is computed with the Haversine formula, "
    "Equation (1), where φ is latitude, λ is longitude in radians and *R* = 6371.0088 km is the mean "
    "Earth radius."))
eq1 = (mr("d(u,v)=2R ") + mfunc("arcsin", mparen(mrad(
    msup(mr("sin", True), mr("2")) + mparen(mfrac(mr("Δφ"), mr("2"))) + mr("+") +
    mfunc("cos", msub(mr("φ"), mr("u"))) + mfunc("cos", msub(mr("φ"), mr("v"))) +
    msup(mr("sin", True), mr("2")) + mparen(mfrac(mr("Δλ"), mr("2")))))))
add(equation(eq1, 1))
add(para(
    "Because buses and trains do not travel in straight lines, the edge weight multiplies this distance "
    "by a circuity factor κ_{m} that depends on the mode *m*: 1.20 for road corridors (the urban road "
    "factor), 1.10 for rail and 1.30 for the walking link, Equation (2). The cost of a path "
    "*P* = (*v*_{0}, *v*_{1}, …, *v*_{k}) is the sum of its edge weights, Equation (3), and its hop count "
    "is *k*."))
add(equation(mr("w(u,v)=") + msub(mr("κ"), mr("m")) + mr("·d(u,v)"), 2))
add(equation(mr("C(P)=") + msum(mr("i=1"), mr("k"), mr("w(") + msub(mr("v"), mr("i−1")) + mr(",") +
                                 msub(mr("v"), mr("i")) + mr(")")), 3))
add(para(
    "The number of transfers *T*(*P*) is the number of times a passenger must board a different corridor. "
    "Since two stops can be joined by several corridors (Gladag–Benteng Vastenburg is served by K1 and "
    "K3, for instance), *T*(*P*) is computed by dynamic programming that chooses one corridor per edge so "
    "that boardings are minimised; walking edges are not counted as boardings. A penalised cost, "
    "Equation (4), adds λ_{T} kilometres per transfer and is used in Section 4.3."))
add(equation(msub(mr("C"), mr("λ")) + mr("(P)=C(P)+") + msub(mr("λ"), mr("T")) + mr("·T(P)"), 4))
add(para(
    "Two simplifications follow from the map. One-way loops and stops served in only one direction were "
    "modelled as undirected edges, and the model contains no timetable, so waiting time is not "
    "represented."))

add(end_section(True))
add(image("rIdFig1", 6.9, 6.9 * FIG1_H / FIG1_W, "Figure 1"))
add(caption_below("Figure", 1, "Weighted Surakarta transit graph on geocoded stop coordinates: (a) whole "
                  "network, (b) city centre. Corridors sharing a road are drawn side by side; dashed lines "
                  "are rail and walking edges. Stop coordinates © OpenStreetMap contributors"))
add(end_section(False))

add(h2("Algorithmic Design (BFS, DFS and Branch-and-Bound)"))
add(para(
    "All algorithms run on an adjacency list built from edges.csv, so neighbours are visited in file "
    "order. BFS (Algorithm 1) explores the graph level by level with a first-in-first-out queue and a "
    "parent map, and stops as soon as the target is removed from the queue. Because every edge counts as "
    "one hop, the first path found has the minimum number of stops. Each vertex and edge is processed at "
    "most once, so the time complexity is *O*(|*V*| + |*E*|) and the queue and parent map need "
    "*O*(|*V*|) space."))
add(pseudocode("Algorithm 1. BFS(G, s, t)", [
    "parent[s] <- NIL; Q <- queue(s)",
    "while Q not empty:",
    "    u <- Q.dequeue(); visited += 1",
    "    if u = t: return path(parent, t)",
    "    for v in Adj[u]:",
    "        if v not in parent:",
    "            parent[v] <- u; Q.enqueue(v)",
    "    peak <- max(peak, |Q|)",
    "return NOT FOUND"]))
add(spacer(80))
add(para(
    "DFS was implemented recursively with a visited set: from the current stop it follows the first "
    "unvisited neighbour as deep as possible and backtracks only at dead ends, returning the first path "
    "that reaches the target. Its time complexity is also *O*(|*V*| + |*E*|), and its memory is the "
    "recursion stack, whose depth can reach *O*(|*V*|). DFS guarantees neither the fewest stops nor the "
    "shortest distance; the route it returns depends on the order in which neighbours are listed."))
add(para(
    "The least-cost Branch-and-Bound algorithm (Algorithm 2) treats every partial route as a live node "
    "with accumulated cost *g*(*x*) and ranks live nodes in a min-priority queue by the bound in "
    "Equation (5), where *h*(*x*) is the straight-line distance from the last stop of *x* to the "
    "target *t*."))
add(equation(mr("f(x)=g(x)+h(x),  h(x)=d(x,t)"), 5))
add(para(
    "Because every weight is at least the straight-line distance between its end stops (κ_{m} ≥ 1) and "
    "straight-line distance obeys the triangle inequality, *h* never overestimates the remaining cost, so "
    "*f*(*x*) is a valid lower bound. A branch is pruned when its bound is not smaller than the incumbent "
    "*U* (the best complete route found so far) or when its cost is not smaller than the best cost "
    "already recorded for the same state (dominance). The search ends when the smallest bound in the "
    "queue cannot improve on *U*, which guarantees that the returned route has minimum distance. With "
    "λ_{T} = 0 a state is a stop; with λ_{T} > 0 a state is a pair (stop, last corridor ridden) so that "
    "transfers can be charged exactly. In the worst case the search behaves like Dijkstra's algorithm, "
    "*O*((|*V*| + |*E*|) log |*V*|) time and *O*(|*V*|) space on the stop graph, with the state space "
    "multiplied by the number of corridors when λ_{T} > 0. Dijkstra's algorithm was implemented as a "
    "reference to verify optimality."))
add(pseudocode("Algorithm 2. LC-BranchAndBound(G, s, t)", [
    "U <- inf; best_g[s] <- 0; PQ <- {(h(s), 0, s)}",
    "while PQ not empty:",
    "    (f, g, x) <- PQ.pop_min()",
    "    if f >= U: break            # bound",
    "    if g > best_g[x]: continue   # stale",
    "    visited += 1",
    "    if x = t: U <- g; incumbent <- x; continue",
    "    for (y, w, c) in Adj[x]:",
    "        g' <- g + w (+ penalty if c changes)",
    "        if g' + h(y) >= U or g' >= best_g[y]:",
    "            pruned += 1; continue",
    "        best_g[y] <- g'; parent[y] <- x",
    "        PQ.push((g' + h(y), g', y))",
    "return path(parent, incumbent), U"]))
add(spacer(80))

add(h2("Experimental Setup and Evaluation Metrics"))
add(para(
    "Fifteen origin-destination scenarios covering the whole metropolitan network were defined "
    "(Table 2). Their category was fixed by the minimum number of transfers the network allows, computed "
    "with B&B and a very large transfer penalty: five short routes need no transfer, five medium routes "
    "need one, and five long routes need at least two."))
t2 = [[r["route_id"], r["origin"], r["destination"], r["min_transfers"], r["straight_line_km"]]
      for r in SCEN]
add(caption("Table", 2, "Route scenarios (direct km = straight-line distance)"))
add(table(["ID", "Origin", "Destination", "Min. transfers", "Direct km"], t2,
          [420, 1500, 1500, 760, 620], size=14, align=["center", "left", "left", "center", "center"]))
add(spacer(80))
add(para("Six metrics were recorded for every algorithm and route:"))
for b in [
        "total distance *C*(*P*) in km, Equation (3), the primary weighted metric;",
        "total stops (hops) *k*;",
        "transfers *T*(*P*);",
        "visited nodes, the number of vertices (or states) removed from the frontier and expanded;",
        "peak memory footprint, measured as the maximum queue length for BFS, the maximum recursion "
        "depth for DFS and the maximum priority-queue length for B&B and Dijkstra, together with the "
        "peak allocation reported by Python's tracemalloc;",
        "execution time per query in microseconds (µs)."]:
    add(bullet(b))
add(para(
    f"The code was written in Python {PY_VER} using only the standard library and run on a Linux "
    f"virtual machine ({CPU}). Each time is the median of {REPS} runs after 20 warm-up runs, with the "
    "garbage collector disabled during timing. Two further experiments were run: B&B with transfer "
    "penalties λ_{T} of 0, 1, 2.5 and 5 km, and DFS with 50 random neighbour orders (seed 2026) to "
    "measure how strongly its result depends on the adjacency order. The dataset, code and raw outputs "
    "are provided with the paper so that every number can be reproduced."))

# ---------------------------------------------------------------- 4
add(h1("RESULT"))
add(h2("Route Distance, Stops and Transfers"))
add(para(
    "Table 3 lists the routes found on every scenario. B&B returned exactly the same distance as "
    "Dijkstra's algorithm on all 15 routes, confirming that the bound-based pruning never discarded the "
    f"optimal route. Across the 15 routes B&B averaged {f2(sm('B&B', 'mean_km'))} km, "
    f"{f1(sm('B&B', 'mean_hops'))} stops and {f1(sm('B&B', 'mean_transfers'))} transfers."))

add(end_section(True))
hdr_rows = [[("Route", 1), ("Stops (hops)", 3), ("Distance (km)", 3), ("Transfers", 3)]]
sub = ["", "BFS", "DFS", "B&B", "BFS", "DFS", "B&B", "BFS", "DFS", "B&B"]
t3 = []
for i in IDS:
    t3.append([i] + [D[(i, a)]["hops"] for a in ALGS] + [D[(i, a)]["distance_km"] for a in ALGS] +
              [D[(i, a)]["transfers"] for a in ALGS])
add(caption("Table", 3, "Path quality per route (B&B distances are identical to Dijkstra on every route)"))
add(table(sub, t3, [900] + [1020] * 9, size=15, header_rows=hdr_rows))
add(spacer(60))
hdr_rows4 = [[("Route", 1), ("Visited nodes", 4), ("Peak frontier", 4), ("Median time (µs)", 4)]]
sub4 = [""] + ["BFS", "DFS", "B&B", "Dijk."] * 3
t4 = []
for i in IDS:
    t4.append([i] + [D[(i, a)]["visited_nodes"] for a in ALGS + ("Dijkstra",)] +
              [D[(i, a)]["peak_frontier"] for a in ALGS + ("Dijkstra",)] +
              [D[(i, a)]["time_us_median"] for a in ALGS + ("Dijkstra",)])
add(caption("Table", 4, "Search effort per route (peak frontier: BFS queue, DFS recursion depth, "
            "B&B and Dijkstra priority queue)"))
add(table(sub4, t4, [720] + [780] * 12, size=15, header_rows=hdr_rows4))
add(spacer(60))
add(end_section(False))

not_opt = [i for i in IDS if i not in bfs_opt]
txt = (f"BFS always found the fewest stops ({f1(sm('BFS', 'mean_hops'))} on average) but returned the "
       f"minimum-distance route only on {num_word(len(bfs_opt))} scenarios ({join_ids(bfs_opt)}). On the "
       f"other {num_word(len(not_opt))} its routes were longer, by {f1(sm('BFS', 'mean_km_gap_vs_optimal_pct'))}% "
       f"on average over all 15 routes and by {f1(gap[worst])}% in the worst case, {worst} "
       f"({ROUTE_NAME[worst]}), where BFS travelled {f2(km[(worst, 'BFS')])} km against "
       f"{f2(km[(worst, 'B&B')])} km. The cause is structural: rail edges are "
       f"{f1(min(rail_means.values()))}–{f1(max(rail_means.values()))} km long on average (Table 1), against "
       f"{f2(statistics.mean(bus_edges))} km for bus edges, but count as a single hop, so BFS uses rail in "
       f"{num_word(len(bfs_rail))} of the 15 routes, whereas the distance-optimal B&B route uses rail in "
       f"{num_word(len(bnb_rail)) if bnb_rail else 'none'}"
       f"{' (' + join_ids(bnb_rail) + ')' if bnb_rail else ''}. ")
r_b, r_k = D[(ex1, "BFS")]["route"], D[(ex1, "B&B")]["route"]
txt += (f"Scenario {ex1} ({ROUTE_NAME[ex1]}) shows the effect clearly. The optimal route rides "
        f"{corridor_list(r_k)} for {hops[(ex1, 'B&B')]} stops and {f2(km[(ex1, 'B&B')])} km with "
        f"{n_tr(trf[(ex1, 'B&B')])}, whereas BFS arrives in "
        f"{hops[(ex1, 'BFS')]} stops but rides {corridor_list(r_b)}, travelling {f2(km[(ex1, 'BFS')])} km "
        f"with {n_tr(trf[(ex1, 'BFS')])}.")
add(para(txt))
txt = (f"Minimising hops also did not minimise transfers. BFS needed {f1(sm('BFS', 'mean_transfers'))} "
       f"transfers per route on average against {f1(sm('B&B', 'mean_transfers'))} for B&B, and more "
       f"transfers than B&B on {num_word(len(bfs_more_tr))} routes ({join_ids(bfs_more_tr)})")
if ex2:
    txt += (f"; it needed fewer only on {join_ids(bfs_less_tr)}. On {ex2}, for example, BFS rides "
            f"{corridor_list(D[(ex2, 'BFS')]['route'])} with {n_tr(trf[(ex2, 'BFS')])}, while the "
            f"shortest route ({f2(km[(ex2, 'B&B')])} km against {f2(km[(ex2, 'BFS')])} km) changes "
            f"{times_word(trf[(ex2, 'B&B')])}.")
else:
    txt += " and never fewer."
add(para(txt))
add(para(
    f"DFS produced by far the worst routes, averaging {f1(sm('DFS', 'mean_hops'))} stops, "
    f"{f2(sm('DFS', 'mean_km'))} km and {f1(sm('DFS', 'mean_transfers'))} transfers; on {dfs_worst} "
    f"({ROUTE_NAME[dfs_worst]}) it wandered through {hops[(dfs_worst, 'DFS')]} stops and "
    f"{f2(km[(dfs_worst, 'DFS')])} km with {trf[(dfs_worst, 'DFS')]} transfers, against "
    f"{f2(km[(dfs_worst, 'B&B')])} km and {trf[(dfs_worst, 'B&B')]} transfers for B&B. The "
    "order-sensitivity experiment confirms that this is a property of the algorithm rather than of the "
    f"chosen adjacency order. Over 50 random orders DFS averaged {f1(sens_mean_hops)} stops and "
    f"{f2(sens_mean_km)} km per route; the best order matched the optimal distance on "
    f"{num_word(sens_best_opt)} of the 15 routes, but the worst reached {sens_max_hops} stops. In a graph "
    "of interlocking corridor loops, the first path that DFS finds is determined by which neighbour "
    "happens to be listed first, not by its cost."))
add(h2("Visited Nodes, Memory Footprint and Execution Time"))
t5 = []
for r in SUMM:
    t5.append([r["category"], r["algorithm"].replace("Dijkstra", "Dijk."), r["mean_km"],
               r["mean_km_gap_vs_optimal_pct"], r["mean_visited"], r["mean_peak_frontier"],
               r["mean_time_us"], r["mean_tracemalloc_kib"]])
add(caption("Table", 5, "Mean results by route category"))
add(table(["Cat.", "Alg.", "km", "Gap %", "Visited", "Peak", "µs", "KiB"], t5,
          [560, 560, 560, 680, 640, 560, 620, 620], size=14))
add(spacer(80))
add(para(
    f"Table 4 and Table 5 show the search effort. BFS expanded {f1(sm('BFS', 'mean_visited'))} nodes per "
    f"query on average, and its queue never held more than {max_peak['BFS']} stops. DFS expanded "
    f"{f1(sm('DFS', 'mean_visited'))} nodes and its recursion depth averaged "
    f"{f1(sm('DFS', 'mean_peak_frontier'))} frames and peaked at {max_peak['DFS']}, because the stack holds "
    "the entire current path; on long, winding paths its memory therefore grows towards *O*(|*V*|), "
    "whereas the BFS queue is bounded by the width of the graph. B&B kept the smallest frontier "
    f"({f1(sm('B&B', 'mean_peak_frontier'))} entries on average) and expanded only "
    f"{f1(sm('B&B', 'mean_visited'))} nodes, {f1(vis_red)}% fewer than Dijkstra's "
    f"{f1(sm('Dijkstra', 'mean_visited'))}, because the straight-line bound prunes branches heading away "
    "from the target. Figure 2 compares the distance and the number of visited nodes for each route."))
add(image("rIdFig2", 3.25, 3.25 * 4.1 / 3.35, "Figure 2"))
add(caption_below("Figure", 2, "Total distance and visited nodes per route"))
times = sorted(ALGS + ("Dijkstra",), key=lambda a: sm(a, "mean_time_us"))
tdesc = ", ".join(f"{a} ({f1(sm(a, 'mean_time_us'))} µs)" for a in times[1:-1])
short_cmp = (f"On short routes B&B ({f1(sm('B&B', 'mean_time_us', 'Short'))} µs) and Dijkstra "
             f"({f1(sm('Dijkstra', 'mean_time_us', 'Short'))} µs) were close. ")
add(para(
    f"Execution time ranks the algorithms differently. {times[0]} was the fastest "
    f"({f1(sm(times[0], 'mean_time_us'))} µs per query on average), followed by {tdesc} and "
    f"{times[-1]} ({f1(sm(times[-1], 'mean_time_us'))} µs). Despite expanding fewer nodes, B&B spends more "
    "time per expansion: each one evaluates a trigonometric Haversine bound and a priority-queue "
    f"operation, and on a graph of {len(NODES)} stops the expansions saved do not repay that cost on "
    "medium and long routes. " + short_cmp + "All queries completed in well under one millisecond, so "
    "for an interactive journey planner the choice of algorithm should be driven by route quality rather "
    "than speed. The advantage of pruning is expected to grow on larger graphs or when expanding a node "
    "is expensive, for example with timetable-dependent weights."))
add(h2("Trade-off between Distance and Transfers"))
pen_rows = [[p, f2(pen_tot[p]["km"]), pen_tot[p]["tr"], pen_tot[p]["hops"], f1(pen_tot[p]["vis"]),
             f1(pen_tot[p]["t"])] for p in PENS]
add(caption("Table", 6, "B&B with a transfer penalty λ_{T} (totals over the 15 routes; time measured in "
            "a separate run)"))
add(table(["λ_{T} (km)", "Total km", "Total transfers", "Total stops", "Mean visited", "Mean µs"],
          pen_rows, [720, 820, 860, 800, 820, 780], size=14))
add(spacer(80))
txt = (f"Table 6 shows how the penalised cost in Equation (4) changes the B&B routes. A penalty of 1 km per "
       f"transfer reduced the total number of transfers over the 15 routes from {pen_tot['0']['tr']} to "
       f"{pen_tot['1']['tr']} (on {join_ids(pen_changed['1'])}) while total distance rose by only "
       f"{f1(pen1_inc)}%, from {f2(pen_tot['0']['km'])} km to {f2(pen_tot['1']['km'])} km.")
if ex3:
    a0, a1 = pen_tot["0"]["rows"][ex3], pen_tot["1"]["rows"][ex3]
    txt += (f" On {ex3} ({ROUTE_NAME[ex3]}), for example, the route changed from "
            f"{corridor_list(a0['route'])} ({a0['distance_km']} km, {n_tr(int(a0['transfers']))}) to "
            f"{corridor_list(a1['route'])} ({a1['distance_km']} km, {n_tr(int(a1['transfers']))}).")
if pen_tot[pen_last]["tr"] < pen_tot["1"]["tr"]:
    txt += (f" Raising the penalty to {first_full} km brought the total down to "
            f"{pen_tot[first_full]['tr']} transfers for a total distance increase of "
            f"{f1((pen_tot[first_full]['km'] / pen_tot['0']['km'] - 1) * 100)}%")
    txt += ", and a 5 km penalty changed nothing further." if first_full != pen_last else "."
else:
    txt += " Larger penalties changed nothing further."
txt += (f" Penalised searches run on the larger (stop, corridor) state space, so they expanded "
        f"{min(vis_ratio):.1f}–{max(vis_ratio):.1f} times as many states and took "
        f"{min(t_ratio):.1f}–{max(t_ratio):.1f} times as long, but they let a planner offer the passenger a "
        "route that is almost as short with fewer changes.")
add(para(txt))
add(h2("Discussion and Limitations"))
add(para(
    "The results agree with earlier Indonesian studies that BFS is fast and yields efficient routes in "
    f"hop terms {C('bernov, darip, prasetyo')} and that DFS explores deep, alternative paths "
    f"{C('darip, prasetyo')}. They add a finding that small, single-mode graphs do not reveal: on a "
    "multi-corridor network with mixed stop spacing, the fewest stops and the shortest distance diverge "
    "sharply because long rail edges and short urban bus edges both count as one hop. Hop-based and "
    "distance-based routing should therefore not be treated as interchangeable, which supports the "
    f"separate treatment of distance and transfers in journey-planning research {C('baum, srikanth')}."))
add(para(
    "The study has limitations. Edge weights are straight-line distances scaled by a fixed circuity "
    "factor rather than distances along the actual road network, and stops without a geocoded landmark "
    "were interpolated, so absolute distances may differ from real ones by a few hundred metres; the "
    "relative comparison between algorithms is unaffected because all of them use the same weights. "
    "Directed loops, timetables, waiting time, walking transfers other than the three interchange walks "
    "and "
    "the Trans Jateng routes were not modelled, and the timings come from a Python implementation on one "
    "machine."))

# ---------------------------------------------------------------- 5
add(h1("CONCLUSION"))
add(para(
    "This study abstracted the 2026 Surakarta public transport integration map into a weighted graph of "
    f"{len(NODES)} stops and {len(EDGES)} corridor edges and compared BFS, DFS and least-cost "
    "Branch-and-Bound on 15 route scenarios. B&B always found the minimum-distance route, matching "
    f"Dijkstra's algorithm, with a mean of {f2(sm('B&B', 'mean_km'))} km and "
    f"{f1(sm('B&B', 'mean_transfers'))} transfers, and it expanded {f1(vis_red)}% fewer nodes than "
    f"Dijkstra. BFS found the fewest stops and was the fastest ({f1(sm('BFS', 'mean_time_us'))} µs), but "
    f"its routes were {f1(sm('BFS', 'mean_km_gap_vs_optimal_pct'))}% longer on average and needed more "
    "transfers, because hop counting favours long rail edges. DFS returned long, order-dependent routes "
    f"averaging {f2(sm('DFS', 'mean_km'))} km and is unsuitable for passenger routing. A transfer penalty "
    f"of 1 km reduced transfers by {(1 - pen_tot['1']['tr'] / pen_tot['0']['tr']) * 100:.0f}% for a "
    f"{f1(pen1_inc)}% increase in distance. For a Surakarta journey planner, distance-weighted B&B with a "
    "small transfer penalty is therefore recommended, with BFS reserved for fast queries in which only "
    "the number of stops matters."))
add(para(
    "Future work should use road-network distances and field-verified positions for the interpolated "
    "stops, model the direction of one-way loops, add time-dependent weights from timetables and waiting "
    "times, include Trans Jateng and walking transfers between nearby stops, compare B&B with A∗ and "
    "multicriteria Pareto search, and deploy the planner as a mobile application for BST passengers."))

REFS = {
    "kartoirono": 'S. Kartoirono, I. Riadi, F. Furizal, and A. Azhari, "Improved breadth first search for '
                  'public transit line search optimization," *Mobile and Forensics*, vol. 5, no. 1, '
                  'pp. 12–22, 2023, doi: 10.12928/mf.v5i1.7906.',
    "bernov": 'M. F. Bernov, A. D. Rahajoe, and B. M. Mulyo, "Route optimization of waste carrier truck '
              'using breadth first search (BFS) algorithm," *JEECS (J. Electr. Eng. Comput. Sci.)*, '
              'vol. 7, no. 2, pp. 1293–1304, Dec. 2022, doi: 10.54732/jeecs.v7i2.23.',
    "darip": 'M. Darip, S. Auliana, A. K. Anam, Parimin, and A. Agung, "Comparison of BFS and DFS '
             'algorithm for routes to historical-cultural tourism locations in Banten Province," '
             '*J. Adv. Inf. Ind. Technol.*, vol. 6, no. 2, pp. 113–122, 2024, doi: 10.52435/jaiit.v6i2.560.',
    "prasetyo": 'T. B. Prasetyo, N. L. D. Sintiari, and K. Telaumbanua, "Analisis komparatif pola traversal '
                'BFS dan DFS pada graf jaringan jalan nyata untuk sistem distribusi kurir," *Jurnal Sifo '
                'Mikroskil*, vol. 27, no. 1, 2026, doi: 10.55601/jsm.v27i1.1941.',
    "lin": 'F. Lin and H.-P. Hsieh, "Multicriteria route planning for in-operation mass transit under urban '
           'data," *Appl. Sci.*, vol. 12, no. 6, Art. no. 3127, 2022, doi: 10.3390/app12063127.',
    "baum": 'M. Baum, V. Buchhold, J. Sauer, D. Wagner, and T. Zündorf, "ULTRA: Unlimited transfers for '
            'efficient multimodal journey planning," *Transp. Sci.*, vol. 57, no. 6, pp. 1536–1559, 2023, '
            'doi: 10.1287/trsc.2022.0198.',
    "srikanth": 'M. Srikanth, A. Pandey, and G. Ramakrishna, "Efficient data structure and algorithms for '
                'minimum transfers in public transportation network," in *Proc. 16th Int. Conf. '
                'Contemporary Computing (IC3-2024)*, Noida, India, 2024, pp. 234–242, '
                'doi: 10.1145/3675888.3676057.',
    "mardiani": 'H. P. Mardiani and A. Widayanti, "Perencanaan rute angkutan pariwisata di Kota Surabaya '
                'metode algoritma Dijkstra," *MITRANS: J. Media Publikasi Terapan Transportasi*, vol. 4, '
                'no. 2, pp. 539–546, Aug. 2026, doi: 10.26740/mitrans.v4n2.p539-546.',
    "syaharini": 'J. S. Syaharini, A. P. Wijaya, and Y. Prasetyo, "Analysis of Batik Solo Trans service area '
                 'to schools and settlements in Surakarta City," *Jurnal Planologi*, vol. 21, no. 1, '
                 'pp. 77–85, 2024, doi: 10.30659/jpsa.v21i1.33217.',
    "xiao": 'Y. Xiao, Z. Zhong, and R. Sun, "Analysis of topological properties and robustness of urban '
            'public transport networks," *Sustainability*, vol. 16, no. 15, Art. no. 6527, 2024, '
            'doi: 10.3390/su16156527.',
}


# ================================================================== ASSEMBLE
def main():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    with zipfile.ZipFile(TEMPLATE_DOCX) as z:
        z.extractall(OUT_DIR)
    doc_path = os.path.join(OUT_DIR, "word", "document.xml")
    s = open(doc_path, encoding="utf-8").read()
    head, rest = s.split("<w:body>", 1)
    parts = re.findall(r'<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>|<w:sectPr.*?</w:sectPr>', rest, flags=re.S)

    # title
    title_p = re.sub(r'(<w:pPr>.*?</w:pPr>).*</w:p>',
                     lambda m: m.group(1) + f'<w:r><w:t xml:space="preserve">{escape(TITLE)}</w:t></w:r></w:p>',
                     parts[0], flags=re.S)
    front = [title_p] + parts[1:14]   # authors block unchanged
    abstract = [parts[14],
                f'<w:p><w:pPr><w:pStyle w:val="Abstract"/></w:pPr>{runs(ABSTRACT, "<w:i/><w:iCs/>")}</w:p>',
                parts[16],
                f'<w:p><w:pPr><w:spacing w:after="120"/></w:pPr>{runs(KEYWORDS)}</w:p>']
    body_xml = "".join(body)
    refs = [parts[56]]
    for k in CITE_ORDER:
        refs.append(f'<w:p><w:pPr><w:pStyle w:val="References"/></w:pPr>{runs(REFS[k], size=None)}</w:p>')
    unused = set(REFS) - set(CITE_ORDER)
    assert not unused, unused
    tail = [parts[62], parts[63], parts[64]]
    new = head + "<w:body>" + "".join(front + abstract) + body_xml + "".join(refs + tail) + "</w:body></w:document>"
    if 'xmlns:m=' not in head:
        raise SystemExit("math namespace missing")
    open(doc_path, "w", encoding="utf-8").write(new)

    # media + relationships
    media = os.path.join(OUT_DIR, "word", "media")
    shutil.copy(os.path.join(PROJ, "figures", "paper_fig1_network.png"), os.path.join(media, "fig1.png"))
    shutil.copy(os.path.join(PROJ, "figures", "paper_fig2_distance_visited.png"), os.path.join(media, "fig2.png"))
    rel_path = os.path.join(OUT_DIR, "word", "_rels", "document.xml.rels")
    rels = open(rel_path, encoding="utf-8").read()
    rels = rels.replace('<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.emf"/>', '')
    rels = rels.replace("</Relationships>",
                        '<Relationship Id="rIdFig1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig1.png"/>'
                        '<Relationship Id="rIdFig2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig2.png"/>'
                        "</Relationships>")
    open(rel_path, "w", encoding="utf-8").write(rels)
    os.remove(os.path.join(media, "image1.emf"))
    ct_path = os.path.join(OUT_DIR, "[Content_Types].xml")
    ct = open(ct_path, encoding="utf-8").read()
    if 'Extension="png"' not in ct:
        ct = ct.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)
    open(ct_path, "w", encoding="utf-8").write(ct)

    if os.path.exists(OUT_DOCX):
        os.remove(OUT_DOCX)
    with zipfile.ZipFile(OUT_DOCX, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(OUT_DIR):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, OUT_DIR))
    shutil.rmtree(OUT_DIR)
    print("written", OUT_DOCX, "citations:", CITE_ORDER)


if __name__ == "__main__":
    main()
