# Presentation outline and team plan

## Slide outline (9 slides)

1. **Title.** Paper title, three names and NIMs, course, target journal (ITSmart, jurnal.uns.ac.id/itsmart) and the repository link (the lecturer asks for both on the slides).
2. **Problem.** Surakarta's 2026 network: BST K1-K5, feeder F7-F12, KRL, KA Bandara, Batara Kresna. Stop spacing ranges from under 0.1 km to 8.6 km, so "fewest stops" is not "shortest trip". Show the official map next to the question: *which algorithm finds the route a passenger actually wants?*
3. **Graph model.** G = (V, E, W): 317 stops, 449 corridor edges, 91 interchange stops; coordinates from OpenStreetMap. Haversine x circuity factor (1.2 bus, 1.1 rail). Show Figure 1 and one row of nodes.csv / edges.csv.
4. **Algorithms.** BFS (queue, min hops), DFS (recursion, first path), LC Branch-and-Bound (priority queue, bound f = g + straight-line distance, prune if f >= incumbent). Complexity table: O(V+E), O(V+E), O((V+E) log V).
5. **Experiment.** The 15 routes (Table 2) on a small map, the six metrics, environment (Python 3.13, median of 300 runs).
6. **Result 1: route quality.** Figure 2(a) and the headline numbers: B&B 9.03 km, BFS 12.14 km (+35.2%), DFS 45.09 km. Worked example S5 Kleco -> Gladag: B&B stays on K1 (6.16 km, no transfers); BFS rides K1, K2, the Batara Kresna railbus, F10 and K3 (9.77 km, 4 transfers).
7. **Result 2: search effort.** Figure 2(b) and Table 5: visited nodes (B&B 72.6 vs Dijkstra 155.9), peak frontier (DFS depth 166), time (BFS 30.1 µs, B&B 166.0 µs) and why B&B is slower despite fewer expansions.
8. **Result 3: transfer penalty.** Table 6: 1 km penalty -> transfers 20 -> 16 for +1.5% distance. Example M3 Purwosari -> Taman Lansia before and after.
9. **Conclusion and future work.** Recommendation (B&B + small penalty for passengers, BFS for quick hop queries, DFS not for routing), limitations, future work. Optional live demo: `python src/benchmark.py --reps 20`.

Keep one idea per slide, put numbers in large type, and keep the detailed tables in a backup slide.

## Team checklist

### Teammate A: data, code and repository
- [ ] Compare every corridor sequence in `data/build_dataset.py` with the 2026 map and fix any stop order or name you disagree with.
- [ ] Spot-check the 69 interpolated stops (`coord_source = interpolated` in nodes.csv) on Google Maps; if one is clearly misplaced, add its real position to `OSM_EXTRA` in `data/build_dataset.py`.
- [ ] If data changed: run `python data/build_dataset.py`, `python src/benchmark.py`, `python src/paper_figures.py`, `python paper/build_paper.py`, then tell Teammate B which numbers in the text changed (tables update automatically, prose does not).
- [ ] Create a public GitHub repository, push this folder, and send the link for slide 1 and the submission email.
- [ ] Prepare a 1-minute live demo of `benchmark.py` for slide 9.

### Teammate B: paper, slides and submission
- [ ] Fill in names, affiliations and emails for authors 2 and 3 in the paper header.
- [ ] Open every DOI in `LITERATURE.md` to confirm it resolves; take the page numbers of reference [7] (Prasetyo et al., 2026) from its PDF.
- [ ] Ask the lecturer whether IEEE numeric references are acceptable: the template text says "Harvard" while its own reference list is numbered.
- [ ] Proofread for British spelling and check the paper stays between 5 and 8 pages in Word (equations add some height).
- [ ] Build the slides from the outline above, using the figures in `figures/`.
- [ ] Add the journal link (jurnal.uns.ac.id/itsmart) to the slides or a .txt file, as the assignment asks.
- [ ] Zip the source code (or repo link), the paper and the slides, and email them to the lecturer no later than one day before meeting 15.

### Everyone
- [ ] Each member can explain one algorithm and its complexity in their own words.
- [ ] Rehearse once with a timer.
- [ ] Optional: submit the paper to ITSmart.
