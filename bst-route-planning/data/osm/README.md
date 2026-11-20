# Stop coordinates from OpenStreetMap

1. `geocode_pass1.ps1` (Windows PowerShell, run 4 workers: `-Worker 0..3 -Workers 4`) geocodes every stop in
   `stops.txt` with OpenStreetMap Nominatim inside the Surakarta bounding box (about 1 request per second overall).
2. `geocode_pass2_retry.ps1` retries stops that failed or matched poorly (`stops_retry.txt`).
3. `geocode_pass3_hubs.ps1` runs hand-written searches for a few hubs (stations, markets); the matches used are
   listed in `OSM_EXTRA` in `../build_dataset.py`.
4. `python select_osm_matches.py` picks one feature per stop and writes `../osm_geocoded_stops.csv`.

Raw Nominatim answers are kept in `raw/` so the selection can be re-run without querying again.
Data © OpenStreetMap contributors, ODbL.
