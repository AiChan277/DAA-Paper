# BFS vs DFS vs Branch-and-Bound on the Surakarta transit network

Final project, Algorithm Design and Analysis (S1 Informatika, UNS).
Paper: *Comparative Analysis of Breadth-First Search, Depth-First Search, and Branch-and-Bound Algorithms for Weighted Multi-Corridor Public Transit Route Planning in Surakarta* (target: ITSmart Journal).

## What is in here

```
data/
  build_dataset.py      corridor stop sequences + anchor coordinates -> nodes.csv, edges.csv
  nodes.csv             317 stops: id, name, lat, lon, type, corridors, coord_source (osm / interpolated)
  edges.csv             449 corridor edges: from, to, corridor, mode, haversine_km, factor, distance_km
  osm_geocoded_stops.csv  stops matched to OpenStreetMap features
  osm/                  geocoding scripts, raw Nominatim answers and the match-selection script
src/
  transit_graph.py      graph loader, Haversine, path distance, transfer counting (DP)
  algorithms.py         BFS, DFS (recursive), least-cost Branch and Bound, Dijkstra (reference)
  benchmark.py          runs the 15 route scenarios and writes every table in results/
  paper_figures.py      draws the paper figures from the CSVs (no re-timing)
results/                CSV + Markdown outputs used in Section IV of the paper
figures/                PNG figures
paper/
  build_paper.py        fills the ITSmart template with the text and the CSV tables
  itsmart_template.docx the group's ITSmart template
  Paper_BFS_DFS_BnB_Surakarta_ITSmart.docx
LITERATURE.md           the 10 verified 2022-2026 references with DOIs and summaries
PROJECT_PLAN.md         slide outline and team checklist
```

## How to run

Python 3.10+ is enough for the algorithms (standard library only). `matplotlib` is needed only for figures.

```bash
python data/build_dataset.py      # regenerate nodes.csv / edges.csv (optional)
python src/benchmark.py           # all experiments, ~10 s; --reps 50 for a quicker run
python src/paper_figures.py       # figures for the paper
python paper/build_paper.py       # rebuild the .docx from the template and results
```

## Data source and modelling choices

- Map: *Peta Integrasi Transportasi Umum Surakarta dan Sekitarnya* (Dinas Perhubungan Kota Surakarta & Transport for Solo), edition 2026-10.
- Modelled: BST K1-K5, feeder F7, F8, F9, F10, F12, KRL Yogyakarta-Palur (Solo section), KA Bandara Adi Soemarmo, KA Batara Kresna (Purwosari-Solo Kota) and the Tirtonadi-Solo Balapan skybridge. K6 and FD11 do not appear on the 2026 map. Trans Jateng S1/S2 are excluded.
- F12 does not stop at Gemblegan Sampurna (it turns south before it on the map).
- Stops inside one interchange box are merged (e.g. Jebres bus stop + Solo Jebres station).
- Stop coordinates come from OpenStreetMap (Nominatim): 248 of 317 stops are matched to an OSM bus stop, station or named landmark (see `data/osm/`); the other 69, mostly small kerbside stops, are interpolated between their geocoded neighbours along the corridor.
- Interchanges: Solo Balapan, Palur and Bandara Adi Soemarmo are single vertices; Jebres - Solo Jebres and Luwes Sangkrah - Solo Kota are joined by short walking edges, as is the Tirtonadi - Solo Balapan skybridge.
- Weight `w(u,v) = Haversine(u,v) x factor` with factor 1.20 (bus), 1.10 (rail), 1.30 (walk).
- Loops and one-direction stops are modelled as undirected edges; there is no timetable.

## Metrics

distance (km), hops, transfers (minimum boardings, walking not counted), visited nodes (expanded),
peak frontier (BFS queue / DFS recursion depth / B&B priority queue), tracemalloc peak, median time (µs, 300 runs).

Timings depend on the machine. The numbers in the paper come from the run recorded in `results/environment.txt`.
