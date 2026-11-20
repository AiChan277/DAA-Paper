# Benchmark results

Graph: |V| = 317 stops, |E| = 449 edges.

Python 3.13.18 (CPython), Linux 6.18.44-fc-v553, x86_64, CPU: Intel(R) Xeon(R) Processor @ 2.10GHz; timing = median of 300 runs after 20 warm-up runs, garbage collector disabled during timing.

## Route scenarios

| ID | Category | Origin | Destination | Min transfers | Straight-line km |
|---|---|---|---|---|---|
| S1 | Short | Solo Balapan | Mall Paragon | 0 | 1.42 |
| S2 | Short | Terminal Tirtonadi | Pasar Legi | 0 | 1.05 |
| S3 | Short | Pasar Gede | Pasar Klewer | 0 | 0.82 |
| S4 | Short | Stadion Manahan | Klodran | 0 | 2.41 |
| S5 | Short | Kleco | Gladag | 0 | 5.11 |
| M1 | Medium | Bandara Adi Soemarmo | Stadion Manahan | 1 | 7.89 |
| M2 | Medium | Sub Terminal Pelangi Mojosongo | Solo Balapan | 1 | 3.83 |
| M3 | Medium | Purwosari | Taman Lansia | 1 | 7.10 |
| M4 | Medium | UNS | Pasar Klewer | 1 | 3.35 |
| M5 | Medium | RSUD Ngipang | UNS | 1 | 6.43 |
| L1 | Long | Lapangan Gentan | Bandara Adi Soemarmo | 2 | 8.75 |
| L2 | Long | Kadipiro | Klodran | 2 | 2.46 |
| L3 | Long | Goa Maria | Simpang Sidan | 2 | 9.32 |
| L4 | Long | Tugu Adipura Jurug | Graha Saba Buana | 2 | 6.45 |
| L5 | Long | RSUD Ngipang | Pasar Bekonang | 2 | 11.47 |

## Per-route results

| ID | Alg | Hops | km | Transfers | Visited | Peak frontier | Time (µs) |
|---|---|---|---|---|---|---|---|
| S1 | BFS | 7 | 2.38 | 0 | 101 | 25 | 28.4 |
| S1 | DFS | 72 | 32.37 | 3 | 273 | 143 | 103.6 |
| S1 | B&B | 7 | 2.38 | 0 | 12 | 9 | 40.3 |
| S1 | Dijkstra | 7 | 2.38 | 0 | 42 | 12 | 41.2 |
| S2 | BFS | 7 | 1.74 | 0 | 86 | 25 | 25.3 |
| S2 | DFS | 128 | 65.34 | 8 | 196 | 148 | 66.7 |
| S2 | B&B | 7 | 1.74 | 0 | 16 | 9 | 51.1 |
| S2 | Dijkstra | 7 | 1.74 | 0 | 25 | 10 | 25.4 |
| S3 | BFS | 7 | 1.58 | 0 | 45 | 21 | 15.0 |
| S3 | DFS | 97 | 53.76 | 10 | 198 | 103 | 61.9 |
| S3 | B&B | 7 | 1.58 | 0 | 12 | 7 | 44.6 |
| S3 | Dijkstra | 7 | 1.58 | 0 | 30 | 13 | 18.7 |
| S4 | BFS | 9 | 4.78 | 0 | 65 | 16 | 12.3 |
| S4 | DFS | 32 | 15.83 | 1 | 312 | 149 | 84.9 |
| S4 | B&B | 9 | 4.78 | 0 | 21 | 5 | 37.6 |
| S4 | Dijkstra | 9 | 4.78 | 0 | 100 | 25 | 58.3 |
| S5 | BFS | 10 | 9.77 | 4 | 87 | 24 | 16.2 |
| S5 | DFS | 43 | 28.61 | 3 | 44 | 44 | 9.5 |
| S5 | B&B | 14 | 6.16 | 0 | 16 | 6 | 32.2 |
| S5 | Dijkstra | 14 | 6.16 | 0 | 69 | 15 | 38.6 |
| M1 | BFS | 8 | 14.62 | 1 | 108 | 28 | 20.1 |
| M1 | DFS | 85 | 39.33 | 5 | 89 | 86 | 19.8 |
| M1 | B&B | 26 | 12.51 | 1 | 42 | 6 | 73.6 |
| M1 | Dijkstra | 26 | 12.51 | 1 | 85 | 12 | 52.6 |
| M2 | BFS | 11 | 6.85 | 2 | 30 | 7 | 8.0 |
| M2 | DFS | 58 | 36.19 | 2 | 59 | 59 | 16.1 |
| M2 | B&B | 15 | 5.83 | 1 | 34 | 6 | 61.7 |
| M2 | Dijkstra | 15 | 5.83 | 1 | 62 | 11 | 32.7 |
| M3 | BFS | 9 | 13.27 | 1 | 152 | 28 | 30.4 |
| M3 | DFS | 72 | 41.03 | 7 | 311 | 117 | 81.9 |
| M3 | B&B | 17 | 8.97 | 2 | 100 | 27 | 217.7 |
| M3 | Dijkstra | 17 | 8.97 | 2 | 261 | 28 | 148.2 |
| M4 | BFS | 15 | 19.22 | 3 | 156 | 22 | 28.1 |
| M4 | DFS | 102 | 55.49 | 9 | 205 | 108 | 42.5 |
| M4 | B&B | 20 | 6.23 | 1 | 54 | 17 | 143.6 |
| M4 | Dijkstra | 20 | 6.23 | 1 | 102 | 17 | 87.7 |
| M5 | BFS | 20 | 14.54 | 2 | 127 | 25 | 33.0 |
| M5 | DFS | 75 | 41.05 | 7 | 281 | 166 | 94.5 |
| M5 | B&B | 24 | 10.15 | 2 | 54 | 13 | 144.9 |
| M5 | Dijkstra | 24 | 10.15 | 2 | 158 | 22 | 133.6 |
| L1 | BFS | 16 | 19.64 | 3 | 52 | 20 | 15.2 |
| L1 | DFS | 34 | 17.51 | 3 | 35 | 35 | 12.1 |
| L1 | B&B | 34 | 17.51 | 3 | 119 | 22 | 307.5 |
| L1 | Dijkstra | 34 | 17.51 | 3 | 313 | 25 | 221.0 |
| L2 | BFS | 15 | 18.47 | 2 | 272 | 28 | 49.1 |
| L2 | DFS | 95 | 52.73 | 7 | 116 | 107 | 25.4 |
| L2 | B&B | 16 | 10.78 | 2 | 85 | 17 | 159.7 |
| L2 | Dijkstra | 16 | 10.78 | 2 | 246 | 23 | 140.8 |
| L3 | BFS | 42 | 16.96 | 2 | 317 | 23 | 56.5 |
| L3 | DFS | 151 | 76.99 | 16 | 262 | 152 | 57.3 |
| L3 | B&B | 43 | 16.17 | 3 | 175 | 20 | 360.7 |
| L3 | Dijkstra | 43 | 16.17 | 3 | 301 | 20 | 170.3 |
| L4 | BFS | 17 | 14.22 | 3 | 241 | 22 | 43.5 |
| L4 | DFS | 90 | 46.15 | 7 | 110 | 105 | 22.8 |
| L4 | B&B | 27 | 12.16 | 3 | 161 | 18 | 365.2 |
| L4 | Dijkstra | 27 | 12.16 | 3 | 231 | 19 | 180.9 |
| L5 | BFS | 43 | 24.01 | 5 | 313 | 26 | 70.1 |
| L5 | DFS | 147 | 73.98 | 8 | 151 | 148 | 40.8 |
| L5 | B&B | 47 | 18.48 | 2 | 188 | 23 | 449.9 |
| L5 | Dijkstra | 47 | 18.48 | 2 | 313 | 22 | 181.6 |

## Summary by category

| category | algorithm | mean_hops | mean_km | mean_km_gap_vs_optimal_pct | mean_transfers | mean_visited | mean_peak_frontier | mean_time_us | mean_tracemalloc_kib |
|---|---|---|---|---|---|---|---|---|---|
| Short | BFS | 8.0 | 4.05 | 11.7 | 0.8 | 76.8 | 22.2 | 19.4 | 6.4 |
| Short | DFS | 74.4 | 39.18 | 1764.9 | 5.0 | 204.6 | 117.4 | 65.3 | 19.0 |
| Short | B&B | 8.8 | 3.33 | 0.0 | 0.0 | 15.4 | 7.2 | 41.2 | 4.2 |
| Short | Dijkstra | 8.8 | 3.33 | 0.0 | 0.0 | 53.2 | 15.0 | 36.4 | 9.0 |
| Medium | BFS | 12.6 | 13.70 | 66.8 | 1.8 | 114.6 | 22.0 | 23.9 | 9.6 |
| Medium | DFS | 78.4 | 42.62 | 437.6 | 6.0 | 189.0 | 107.2 | 51.0 | 19.4 |
| Medium | B&B | 20.4 | 8.74 | 0.0 | 1.4 | 56.8 | 13.8 | 128.3 | 13.3 |
| Medium | Dijkstra | 20.4 | 8.74 | 0.0 | 1.4 | 133.6 | 18.0 | 90.9 | 22.5 |
| Long | BFS | 26.6 | 18.66 | 27.0 | 3.0 | 239.0 | 23.8 | 46.9 | 12.7 |
| Long | DFS | 103.4 | 53.47 | 269.0 | 8.2 | 134.8 | 109.4 | 31.7 | 13.5 |
| Long | B&B | 33.4 | 15.02 | 0.0 | 2.6 | 145.6 | 20.0 | 328.6 | 38.9 |
| Long | Dijkstra | 33.4 | 15.02 | 0.0 | 2.6 | 280.8 | 21.8 | 178.9 | 45.0 |
| All | BFS | 15.7 | 12.14 | 35.2 | 1.9 | 143.5 | 22.7 | 30.1 | 9.6 |
| All | DFS | 85.4 | 45.09 | 823.8 | 6.4 | 176.1 | 111.3 | 49.3 | 17.3 |
| All | B&B | 20.9 | 9.03 | 0.0 | 1.3 | 72.6 | 13.7 | 166.0 | 18.8 |
| All | Dijkstra | 20.9 | 9.03 | 0.0 | 1.3 | 155.9 | 18.3 | 102.1 | 25.5 |

## Branch and Bound with transfer penalty

| ID | Penalty km | Hops | km | Transfers | Visited states | Time (µs) |
|---|---|---|---|---|---|---|
| S1 | 0 | 7 | 2.38 | 0 | 12 | 27.9 |
| S1 | 1 | 7 | 2.38 | 0 | 13 | 32.3 |
| S1 | 2.5 | 7 | 2.38 | 0 | 13 | 33.2 |
| S1 | 5 | 7 | 2.38 | 0 | 13 | 32.4 |
| S2 | 0 | 7 | 1.74 | 0 | 16 | 33.9 |
| S2 | 1 | 7 | 1.74 | 0 | 19 | 41.8 |
| S2 | 2.5 | 7 | 1.74 | 0 | 19 | 42.5 |
| S2 | 5 | 7 | 1.74 | 0 | 19 | 41.7 |
| S3 | 0 | 7 | 1.58 | 0 | 12 | 32.7 |
| S3 | 1 | 7 | 1.58 | 0 | 28 | 82.9 |
| S3 | 2.5 | 7 | 1.58 | 0 | 28 | 81.5 |
| S3 | 5 | 7 | 1.58 | 0 | 28 | 82.6 |
| S4 | 0 | 9 | 4.78 | 0 | 21 | 37.7 |
| S4 | 1 | 9 | 4.78 | 0 | 25 | 49.3 |
| S4 | 2.5 | 9 | 4.78 | 0 | 25 | 49.1 |
| S4 | 5 | 9 | 4.78 | 0 | 25 | 48.4 |
| S5 | 0 | 14 | 6.16 | 0 | 16 | 32.6 |
| S5 | 1 | 14 | 6.16 | 0 | 16 | 39.1 |
| S5 | 2.5 | 14 | 6.16 | 0 | 16 | 39.6 |
| S5 | 5 | 14 | 6.16 | 0 | 16 | 38.9 |
| M1 | 0 | 26 | 12.51 | 1 | 42 | 73.6 |
| M1 | 1 | 26 | 12.51 | 1 | 53 | 111.5 |
| M1 | 2.5 | 26 | 12.51 | 1 | 70 | 143.7 |
| M1 | 5 | 26 | 12.51 | 1 | 75 | 161.6 |
| M2 | 0 | 15 | 5.83 | 1 | 34 | 81.6 |
| M2 | 1 | 15 | 5.83 | 1 | 51 | 108.8 |
| M2 | 2.5 | 15 | 5.83 | 1 | 53 | 147.8 |
| M2 | 5 | 15 | 5.83 | 1 | 60 | 166.7 |
| M3 | 0 | 17 | 8.97 | 2 | 100 | 282.5 |
| M3 | 1 | 15 | 9.66 | 1 | 158 | 436.5 |
| M3 | 2.5 | 15 | 9.66 | 1 | 147 | 407.3 |
| M3 | 5 | 15 | 9.66 | 1 | 150 | 415.0 |
| M4 | 0 | 20 | 6.23 | 1 | 54 | 125.3 |
| M4 | 1 | 20 | 6.23 | 1 | 111 | 399.4 |
| M4 | 2.5 | 20 | 6.23 | 1 | 124 | 366.6 |
| M4 | 5 | 20 | 6.23 | 1 | 134 | 386.1 |
| M5 | 0 | 24 | 10.15 | 2 | 54 | 110.3 |
| M5 | 1 | 28 | 10.56 | 1 | 87 | 229.3 |
| M5 | 2.5 | 28 | 10.56 | 1 | 91 | 236.2 |
| M5 | 5 | 28 | 10.56 | 1 | 94 | 258.2 |
| L1 | 0 | 34 | 17.51 | 3 | 119 | 259.5 |
| L1 | 1 | 34 | 17.51 | 3 | 176 | 369.7 |
| L1 | 2.5 | 34 | 17.51 | 3 | 249 | 553.2 |
| L1 | 5 | 44 | 20.41 | 2 | 283 | 702.6 |
| L2 | 0 | 16 | 10.78 | 2 | 85 | 163.2 |
| L2 | 1 | 16 | 10.78 | 2 | 131 | 289.7 |
| L2 | 2.5 | 16 | 10.78 | 2 | 163 | 561.0 |
| L2 | 5 | 16 | 10.78 | 2 | 215 | 602.0 |
| L3 | 0 | 43 | 16.17 | 3 | 175 | 363.9 |
| L3 | 1 | 42 | 16.96 | 2 | 315 | 844.4 |
| L3 | 2.5 | 42 | 16.96 | 2 | 327 | 861.7 |
| L3 | 5 | 42 | 16.96 | 2 | 344 | 1188.3 |
| L4 | 0 | 27 | 12.16 | 3 | 161 | 451.9 |
| L4 | 1 | 36 | 12.26 | 2 | 296 | 996.0 |
| L4 | 2.5 | 36 | 12.26 | 2 | 313 | 767.8 |
| L4 | 5 | 36 | 12.26 | 2 | 337 | 825.6 |
| L5 | 0 | 47 | 18.48 | 2 | 188 | 384.1 |
| L5 | 1 | 47 | 18.48 | 2 | 325 | 817.3 |
| L5 | 2.5 | 47 | 18.48 | 2 | 342 | 855.3 |
| L5 | 5 | 47 | 18.48 | 2 | 354 | 873.8 |

## DFS neighbour-order sensitivity (50 random orders)

| ID | min hops | mean hops | max hops | sd | min km | mean km | max km | BFS hops | optimal km |
|---|---|---|---|---|---|---|---|---|---|
| S1 | 7 | 63.0 | 141 | 45.5 | 2.38 | 30.35 | 71.88 | 7 | 2.38 |
| S2 | 7 | 57.2 | 147 | 48.9 | 1.74 | 28.82 | 86.66 | 7 | 1.74 |
| S3 | 7 | 71.7 | 164 | 42.3 | 1.58 | 33.48 | 76.37 | 7 | 1.58 |
| S4 | 9 | 76.2 | 187 | 49.7 | 4.78 | 38.67 | 93.64 | 9 | 4.78 |
| S5 | 10 | 80.8 | 136 | 35.4 | 6.60 | 39.15 | 68.48 | 10 | 6.16 |
| M1 | 9 | 78.2 | 160 | 42.0 | 12.51 | 40.79 | 78.84 | 8 | 12.51 |
| M2 | 11 | 38.1 | 142 | 30.4 | 5.83 | 17.35 | 66.94 | 11 | 5.83 |
| M3 | 21 | 104.2 | 169 | 36.7 | 12.03 | 48.88 | 85.21 | 9 | 8.97 |
| M4 | 35 | 90.5 | 160 | 36.4 | 11.84 | 42.29 | 83.45 | 15 | 6.23 |
| M5 | 20 | 92.8 | 174 | 44.3 | 10.15 | 43.49 | 76.34 | 20 | 10.15 |
| L1 | 34 | 103.2 | 213 | 34.3 | 17.51 | 49.88 | 85.48 | 16 | 17.51 |
| L2 | 15 | 67.1 | 173 | 46.9 | 11.50 | 37.10 | 77.97 | 15 | 10.78 |
| L3 | 53 | 115.4 | 192 | 35.6 | 21.19 | 52.99 | 99.56 | 42 | 16.17 |
| L4 | 20 | 96.1 | 154 | 34.0 | 14.46 | 45.64 | 70.31 | 17 | 12.16 |
| L5 | 47 | 118.8 | 186 | 35.3 | 18.48 | 55.55 | 96.26 | 43 | 18.48 |

## Routes found

| ID | Alg | Route |
|---|---|---|
| S1 | BFS | K2: Solo Balapan -> Mall Paragon |
| S1 | DFS | K2: Solo Balapan -> Panggung | K1: Panggung -> Pasar Colomadu | K5: Pasar Colomadu -> Kota Barat | K2: Kota Barat -> Mall Paragon |
| S1 | B&B | K2: Solo Balapan -> Mall Paragon |
| S1 | Dijkstra | K2: Solo Balapan -> Mall Paragon |
| S2 | BFS | F7: Terminal Tirtonadi -> Pasar Legi |
| S2 | DFS | K4: Terminal Tirtonadi -> Gereja Colomadu | K1: Gereja Colomadu -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Panggung | K1: Panggung -> Luwes Kartasura | K4: Luwes Kartasura -> Terminal Kartasura | K3: Terminal Kartasura -> Simpang 3 Notosuman Timur | K5: Simpang 3 Notosuman Timur -> Simpang Notosuman Barat | F9: Simpang Notosuman Barat -> Pasar Legi |
| S2 | B&B | F7: Terminal Tirtonadi -> Pasar Legi |
| S2 | Dijkstra | F7: Terminal Tirtonadi -> Pasar Legi |
| S3 | BFS | K3: Pasar Gede -> Pasar Klewer |
| S3 | DFS | K1: Pasar Gede -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Panggung | K1: Panggung -> Warung Pelem | F7: Warung Pelem -> Pasar Legi | F9: Pasar Legi -> Simpang 3 Notosuman Timur | K3: Simpang 3 Notosuman Timur -> Pasar Jongke | F12: Pasar Jongke -> Simpang Batikan | K2: Simpang Batikan -> Purwosari | BK: Purwosari -> Solo Kota | WALK: Solo Kota -> Luwes Sangkrah | F10: Luwes Sangkrah -> Pasar Klewer |
| S3 | B&B | K3: Pasar Gede -> Pasar Klewer |
| S3 | Dijkstra | K3: Pasar Gede -> Pasar Klewer |
| S4 | BFS | K5: Stadion Manahan -> Klodran |
| S4 | DFS | K4: Stadion Manahan -> Gereja Colomadu | K5: Gereja Colomadu -> Klodran |
| S4 | B&B | K5: Stadion Manahan -> Klodran |
| S4 | Dijkstra | K5: Stadion Manahan -> Klodran |
| S5 | BFS | K1: Kleco -> Kasih Ibu | K2: Kasih Ibu -> Purwosari | BK: Purwosari -> Solo Kota | WALK: Solo Kota -> Luwes Sangkrah | F10: Luwes Sangkrah -> Pasar Akik | K3: Pasar Akik -> Gladag |
| S5 | DFS | K1: Kleco -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Panggung | K1: Panggung -> Gladag |
| S5 | B&B | K1: Kleco -> Gladag |
| S5 | Dijkstra | K1: Kleco -> Gladag |
| M1 | BFS | BIAS: Bandara Adi Soemarmo -> Solo Balapan | WALK: Solo Balapan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> Stadion Manahan |
| M1 | DFS | K1: Bandara Adi Soemarmo -> Palur | BIAS: Palur -> Solo Balapan | K2: Solo Balapan -> Margoyudan | F8: Margoyudan -> Kelurahan Stabelan | F7: Kelurahan Stabelan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> Stadion Manahan |
| M1 | B&B | K1: Bandara Adi Soemarmo -> Gereja Colomadu | K4: Gereja Colomadu -> Stadion Manahan |
| M1 | Dijkstra | K1: Bandara Adi Soemarmo -> Gereja Colomadu | K4: Gereja Colomadu -> Stadion Manahan |
| M2 | BFS | F8: Sub Terminal Pelangi Mojosongo -> Panggung | K1: Panggung -> Jebres | WALK: Jebres -> Solo Jebres | BIAS: Solo Jebres -> Solo Balapan |
| M2 | DFS | F8: Sub Terminal Pelangi Mojosongo -> Panggung | K1: Panggung -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan |
| M2 | B&B | F8: Sub Terminal Pelangi Mojosongo -> Margoyudan | K2: Margoyudan -> Solo Balapan |
| M2 | Dijkstra | F8: Sub Terminal Pelangi Mojosongo -> Margoyudan | K2: Margoyudan -> Solo Balapan |
| M3 | BFS | KRL: Purwosari -> Palur | K4: Palur -> Taman Lansia |
| M3 | DFS | K2: Purwosari -> Kasih Ibu | K1: Kasih Ibu -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Panggung | K1: Panggung -> Warung Pelem | F10: Warung Pelem -> ASMI | K1: ASMI -> Thiongting | K3: Thiongting -> Taman Lansia |
| M3 | B&B | KRL: Purwosari -> Solo Balapan | K2: Solo Balapan -> Thiongting | K3: Thiongting -> Taman Lansia |
| M3 | Dijkstra | KRL: Purwosari -> Solo Balapan | K2: Solo Balapan -> Thiongting | K3: Thiongting -> Taman Lansia |
| M4 | BFS | K1: UNS -> Palur | KRL: Palur -> Purwosari | BK: Purwosari -> Solo Kota | WALK: Solo Kota -> Luwes Sangkrah | F10: Luwes Sangkrah -> Pasar Klewer |
| M4 | DFS | K1: UNS -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Margoyudan | F8: Margoyudan -> Pasar Legi | F9: Pasar Legi -> Simpang 3 Notosuman Timur | K3: Simpang 3 Notosuman Timur -> Pasar Jongke | F12: Pasar Jongke -> Simpang Batikan | K2: Simpang Batikan -> Purwosari | BK: Purwosari -> Solo Kota | WALK: Solo Kota -> Luwes Sangkrah | F10: Luwes Sangkrah -> Pasar Klewer |
| M4 | B&B | K1: UNS -> Gladag | K3: Gladag -> Pasar Klewer |
| M4 | Dijkstra | K1: UNS -> Gladag | K3: Gladag -> Pasar Klewer |
| M5 | BFS | F7: RSUD Ngipang -> Terminal Tirtonadi | WALK: Terminal Tirtonadi -> Solo Balapan | BIAS: Solo Balapan -> Palur | K1: Palur -> UNS |
| M5 | DFS | F7: RSUD Ngipang -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> Gereja Colomadu | K1: Gereja Colomadu -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Panggung | K1: Panggung -> Warung Pelem | F10: Warung Pelem -> ASMI | K1: ASMI -> UNS |
| M5 | B&B | F7: RSUD Ngipang -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> Panggung | K1: Panggung -> UNS |
| M5 | Dijkstra | F7: RSUD Ngipang -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> Panggung | K1: Panggung -> UNS |
| L1 | BFS | F12: Lapangan Gentan -> Simpang Batikan | K2: Simpang Batikan -> Purwosari | KRL: Purwosari -> Solo Balapan | BIAS: Solo Balapan -> Bandara Adi Soemarmo |
| L1 | DFS | F12: Lapangan Gentan -> Pasar Jongke | K3: Pasar Jongke -> Terminal Kartasura | K4: Terminal Kartasura -> Luwes Kartasura | K1: Luwes Kartasura -> Bandara Adi Soemarmo |
| L1 | B&B | F12: Lapangan Gentan -> Pasar Jongke | K3: Pasar Jongke -> Terminal Kartasura | K4: Terminal Kartasura -> Luwes Kartasura | K1: Luwes Kartasura -> Bandara Adi Soemarmo |
| L1 | Dijkstra | F12: Lapangan Gentan -> Pasar Jongke | K3: Pasar Jongke -> Terminal Kartasura | K4: Terminal Kartasura -> Luwes Kartasura | K1: Luwes Kartasura -> Bandara Adi Soemarmo |
| L2 | BFS | BIAS: Kadipiro -> Bandara Adi Soemarmo | K1: Bandara Adi Soemarmo -> Pasar Colomadu | K5: Pasar Colomadu -> Klodran |
| L2 | DFS | BIAS: Kadipiro -> Bandara Adi Soemarmo | K1: Bandara Adi Soemarmo -> Palur | BIAS: Palur -> Solo Balapan | K2: Solo Balapan -> Margoyudan | F8: Margoyudan -> Kelurahan Stabelan | F7: Kelurahan Stabelan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> TK Pembina | K5: TK Pembina -> Klodran |
| L2 | B&B | BIAS: Kadipiro -> Solo Balapan | WALK: Solo Balapan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> TK Pembina | K5: TK Pembina -> Klodran |
| L2 | Dijkstra | BIAS: Kadipiro -> Solo Balapan | WALK: Solo Balapan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> TK Pembina | K5: TK Pembina -> Klodran |
| L3 | BFS | F8: Goa Maria -> Panggung | K3: Panggung -> Simpang 3 Notosuman Timur | K5: Simpang 3 Notosuman Timur -> Simpang Sidan |
| L3 | DFS | F8: Goa Maria -> Sub Terminal Pelangi Mojosongo | F9: Sub Terminal Pelangi Mojosongo -> Patung Mayor Achmadi | F8: Patung Mayor Achmadi -> Panggung | K1: Panggung -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Kota Barat | K5: Kota Barat -> Stadion Manahan | K4: Stadion Manahan -> Terminal Tirtonadi | F7: Terminal Tirtonadi -> Pasar Legi | F9: Pasar Legi -> Simpang 3 Notosuman Timur | K3: Simpang 3 Notosuman Timur -> Pasar Jongke | F12: Pasar Jongke -> Simpang Batikan | K2: Simpang Batikan -> Purwosari | BK: Purwosari -> Solo Kota | WALK: Solo Kota -> Luwes Sangkrah | F10: Luwes Sangkrah -> Pasar Klewer | F12: Pasar Klewer -> Simpang Baturono | K5: Simpang Baturono -> Simpang Sidan |
| L3 | B&B | F8: Goa Maria -> Panggung | K3: Panggung -> Pasar Klewer | F12: Pasar Klewer -> Simpang Baturono | K5: Simpang Baturono -> Simpang Sidan |
| L3 | Dijkstra | F8: Goa Maria -> Panggung | K3: Panggung -> Pasar Klewer | F12: Pasar Klewer -> Simpang Baturono | K5: Simpang Baturono -> Simpang Sidan |
| L4 | BFS | F10: Tugu Adipura Jurug -> Palur | BIAS: Palur -> Solo Balapan | WALK: Solo Balapan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> TK Pembina | K5: TK Pembina -> Graha Saba Buana |
| L4 | DFS | F10: Tugu Adipura Jurug -> ASMI | K1: ASMI -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Margoyudan | F8: Margoyudan -> Kelurahan Stabelan | F7: Kelurahan Stabelan -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> TK Pembina | K5: TK Pembina -> Graha Saba Buana |
| L4 | B&B | F10: Tugu Adipura Jurug -> ASMI | K1: ASMI -> Panggung | K4: Panggung -> TK Pembina | K5: TK Pembina -> Graha Saba Buana |
| L4 | Dijkstra | F10: Tugu Adipura Jurug -> ASMI | K1: ASMI -> Panggung | K4: Panggung -> TK Pembina | K5: TK Pembina -> Graha Saba Buana |
| L5 | BFS | F7: RSUD Ngipang -> Terminal Tirtonadi | WALK: Terminal Tirtonadi -> Solo Balapan | KRL: Solo Balapan -> Purwosari | BK: Purwosari -> Solo Kota | WALK: Solo Kota -> Luwes Sangkrah | F10: Luwes Sangkrah -> Pasar Klewer | F12: Pasar Klewer -> Simpang Baturono | K5: Simpang Baturono -> Pasar Bekonang |
| L5 | DFS | F7: RSUD Ngipang -> Terminal Tirtonadi | K4: Terminal Tirtonadi -> Gereja Colomadu | K1: Gereja Colomadu -> Bandara Adi Soemarmo | BIAS: Bandara Adi Soemarmo -> Solo Balapan | K2: Solo Balapan -> Panggung | K1: Panggung -> Luwes Kartasura | K4: Luwes Kartasura -> Terminal Kartasura | K3: Terminal Kartasura -> Simpang 3 Notosuman Timur | K5: Simpang 3 Notosuman Timur -> Pasar Bekonang |
| L5 | B&B | F7: RSUD Ngipang -> Pasar Legi | F9: Pasar Legi -> Sub Terminal Semanggi | K5: Sub Terminal Semanggi -> Pasar Bekonang |
| L5 | Dijkstra | F7: RSUD Ngipang -> Pasar Legi | F9: Pasar Legi -> Sub Terminal Semanggi | K5: Sub Terminal Semanggi -> Pasar Bekonang |
