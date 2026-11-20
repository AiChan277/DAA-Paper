"""
build_dataset.py
----------------
Builds the weighted Surakarta transit graph G = (V, E, W) used in the study and
writes it to nodes.csv and edges.csv.

Source map: "Peta Integrasi Transportasi Umum Surakarta dan Sekitarnya /
Surakarta Metropolitan Public Transportation Integration Map", Dinas Perhubungan
Kota Surakarta & Transport for Solo, edition 2026-10.

How the dataset is built
1. CORRIDORS lists the stop sequence of every corridor exactly as drawn on the
   map (Batik Solo Trans K1-K5, feeder F7-F10 and F12, KRL Yogyakarta-Palur,
   KA Bandara Adi Soemarmo, KA Batara Kresna, plus the Tirtonadi-Balapan
   skybridge). Stops that the map draws inside one interchange (hatched) box
   are merged into one node, e.g. "Solo Jebres" = Jebres bus stop + station.
2. Stop coordinates come from OpenStreetMap: every stop name was geocoded with
   Nominatim inside the Surakarta bounding box, and a match was kept only when
   its name agrees with the stop and it lies on the corridor
   (osm_geocoded_stops.csv, plus OSM_EXTRA below). Stops without a reliable
   match (mostly small kerbside stops) are placed by linear interpolation
   between their geocoded neighbours along the corridor.
3. Edge weight w(u, v) = Haversine(u, v) x circuity factor
   (1.20 for road corridors, 1.10 for rail, 1.30 for the walking link).

Simplifications (documented in the paper): one-way loops and directional
stops are modelled as undirected edges; Trans Jateng S1/S2 are excluded.
Interchanges drawn as one box on the map are merged into one vertex when the
stop and station are the same place, and joined by a walking edge when they
are a few hundred metres apart (Jebres - Solo Jebres, Luwes Sangkrah - Solo
Kota, Terminal Tirtonadi - Solo Balapan skybridge).
"""
import csv
import math
import os

R_EARTH_KM = 6371.0088
FACTOR = {"bus": 1.20, "rail": 1.10, "walk": 1.30}

# --------------------------------------------------------------------------
# Corridor definitions: (corridor_id, mode, corridor_name, [stop sequence])
# Several corridors are given as more than one segment where the map shows a
# loop or a branch (the segments share their end stops).
# --------------------------------------------------------------------------
CORRIDORS = [
    ("K1", "bus", "BST Koridor 1: Terminal Palur - Bandara Adi Soemarmo", [
        "Bandara Adi Soemarmo", "SMPN 1 Ngemplak", "Tanjung Sari", "SMPN 3 Colomadu",
        "Pasar Colomadu", "Gereja Colomadu", "Klegen", "Luwes Kartasura", "RS Karima",
        "Bulog", "SMPN 1 Kartasura", "Singopuran", "Simpang Kartasura",
        "SMP 1 Muhammadiyah Kartasura", "Ngadirejo Pandeyan", "SPBU Gembongan",
        "Gembongan", "Suharti", "Gumpang", "Goro Mall", "SMPN 2 Kartasura", "Transmart",
        "UMS", "RS Yarsis", "RS UNS / RS Ortopedi", "Mendungan", "Kleco", "Faroka",
        "Korem", "Sub Terminal Kerten", "Kasih Ibu", "DKT", "Gendengan", "Sriwedari 1",
        "Sriwedari 2", "Ngapeman", "Timuran", "Kemlayan", "Pasar Pon", "Nonongan",
        "Gladag", "Benteng Vastenburg", "Balai Kota", "Pasar Gede", "Warung Pelem",
        "Urip Sumoharjo", "Mesen", "Jebres", "Panggung", "RS Hermina",
        "RSUD dr. Moewardi", "SMA Muhammadiyah 3", "Thiongting", "Cembengan",
        "Sekarpace", "TBS", "UNS", "TMP", "Jurug", "ASMI", "Mitra Palur", "Palur",
        "Terminal Palur"]),
    ("K2", "bus", "BST Koridor 2: Terminal Palur - Purwosari", [
        "Terminal Palur", "Palur", "Mitra Palur", "ASMI", "Jurug", "TMP", "UNS", "TBS",
        "Sekarpace", "Cembengan", "Thiongting", "SMA Muhammadiyah 3",
        "RSUD dr. Moewardi", "RS Hermina", "Panggung", "Purbowardayan",
        "SMAN 1 Surakarta", "Margoyudan", "TK-SD Cemara 2", "Proliman", "SPBU Balapan",
        "Solo Balapan", "Punggawan", "Wonder", "Monumen Pers", "RS PKU Surakarta",
        "SMA Muhammadiyah 2", "Yosodipuro", "Mall Paragon", "Kota Barat",
        "SMPN 24 Surakarta", "Gendengan", "DKT", "Kasih Ibu", "Purwosari", "UNIBA",
        "Djamaatul Ichwan", "Simpang Batikan", "Aston", "Purwosari"]),
    ("K3", "bus", "BST Koridor 3: Terminal Kartasura - Taman Lansia", [
        "Terminal Kartasura", "Tugu Kartasura", "Polsek Kartasura", "PKU Kartasura",
        "Pasar Kartasura", "Gapura Keraton Kartasura", "Sedahromo",
        "Superindo Gumpang", "Ngadirejo", "Pasar Gumpang", "Tyfountex Barat",
        "Tyfountex Timur", "Proyek Bengawan", "Windan", "Pracimaloyo", "Makamhaji",
        "Tugu Lilin", "Pasar Jongke", "Batik Omah Laweyan", "Pasar Kabangan",
        "dr. Radjiman", "Sabar Motor", "Baron Barat", "Baron", "Kec. Laweyan",
        "BLK Surakarta", "SMAN 7 Surakarta", "Lotte Grosir Tipes", "TASPEN",
        "Serengan", "Widya Wacana", "Gemblegan Sampurna",
        "Simpang 3 Notosuman Timur", "Simpang Kalilarangan", "Batik Keris",
        "Nonongan", "Gladag", "Benteng Vastenburg", "Balai Kota", "Pasar Gede",
        "Warung Pelem", "Urip Sumoharjo", "Mesen", "Jebres", "Panggung",
        "RS Hermina", "RSUD dr. Moewardi", "SMA Muhammadiyah 3", "Thiongting",
        "Universitas Aisyiyah", "ISI Solo Techno Park", "Kecamatan Jebres",
        "UNS Belakang", "Taman Lansia"]),
    ("K3", "bus", "BST Koridor 3 (westbound via Pasar Klewer)", [
        "Gladag", "Pasar Akik", "Alun-Alun Utara", "Polsek Pasar Kliwon",
        "Pasar Klewer", "Coyudan Timur", "Masjid Fatimah", "Pasar Kembang",
        "Kec. Laweyan"]),
    ("K4", "bus", "BST Koridor 4: Terminal Kartasura - Terminal Palur", [
        "Terminal Kartasura", "Luwes Kartasura", "Klegen", "Gereja Colomadu",
        "Kantor Kec. Colomadu", "SPBU Colomadu", "Koramil Colomadu", "YPAC",
        "Jonggrang", "Gajahan IHS", "ATMI", "LOR INN", "Lapangan Blulukan", "Alana",
        "Solo Pos", "DPRD Surakarta", "Adi Sucipto Barat", "Adi Sucipto Timur",
        "Jajar", "Sekolah Ursulin", "SMKN 5 Surakarta", "TK Pembina",
        "RS Bhayangkara", "SMAN 4 Surakarta", "Stadion Manahan",
        "Gedung Wanita / SMPN 1 Surakarta", "PLN Manahan", "RS Brayat", "Dewa Dewi",
        "Terminal Tirtonadi", "Simpang 3 Gilingan", "Masjid Raya Sheikh Zayed",
        "Simpang AUB", "Panggung", "RS Hermina", "RSUD dr. Moewardi",
        "SMA Muhammadiyah 3", "Thiongting", "Universitas Aisyiyah",
        "ISI Solo Techno Park", "Kecamatan Jebres", "UNS Belakang", "Taman Lansia",
        "Rusun Jurug", "Pasar Buah Jurug", "Jurug", "ASMI", "Mitra Palur", "Palur",
        "Terminal Palur"]),
    ("K5", "bus", "BST Koridor 5: Terminal Kartasura - Simpang Sidan", [
        "Terminal Kartasura", "Luwes Kartasura", "Klegen", "Gereja Colomadu",
        "Pasar Colomadu", "GBI Malangjiwan", "Malangjiwan Utara",
        "Gawanan / SMPN 1 Colomadu", "SMK Penerbangan Adi Soemarmo", "Yakkum",
        "Garasi BST Tohudan", "Tohudan Poltekkes", "Gedongan", "Puskesmas Colomadu 2",
        "Klodran", "SMKN 9 Surakarta", "SMPN 23 Surakarta", "Graha Saba Buana",
        "Lapangan Sumber", "SMPN 12 Surakarta", "TK Pembina", "RS Bhayangkara",
        "SMAN 4 Surakarta", "Stadion Manahan", "Kota Barat", "SMPN 24 Surakarta",
        "Gendengan", "Sriwedari 1", "Sriwedari 2", "Ngapeman", "Timuran", "Kemlayan",
        "Pasar Pon", "Batik Keris", "Simpang Kalilarangan",
        "Simpang 3 Notosuman Timur", "Gemblegan", "Simpang Grobakan", "Luwes Gading",
        "Pasar Gading", "Simpang Baturono", "Apil Semanggi", "SPBU Semanggi",
        "Sub Terminal Semanggi", "SMA MTA", "Jembatan Mojo", "Ngebrak", "Laban",
        "Graha Safira", "Pasar Plumbon", "Desa Wisata Wirun", "GTP", "Kel. Wirun",
        "Polsek Mojolaban", "SMAN 1 Mojolaban", "Tugu Bendo", "Pasar Bekonang",
        "Lapangan Cangkol", "SMPN 1 Mojolaban", "SPBU Sidan", "Simpang Sidan"]),
    ("K5", "bus", "BST Koridor 5 (northbound via Singosaren)", [
        "Gemblegan", "Gereja Masjid", "Simpang Notosuman Barat", "Singosaren",
        "Gatot Subroto Ngarsopuro", "Pasar Pon"]),
    ("F7", "bus", "Feeder F7: RSUD Ngipang - Pasar Klewer", [
        "RSUD Ngipang", "GKJ Ngipang", "LDII Bayan Krajan", "Puskesmas Krembyongan",
        "Banyuagung", "Sumpingan", "SD Kristen 2 Stabelan", "SDN 3 Banyuagung",
        "Kimia Farma Banyuagung", "Luwes Nusukan", "Pasar Nusukan",
        "Jembatan Tirtonadi", "Terminal Tirtonadi", "Pasar Papsa Gilingan",
        "Pasar Besi Gilingan", "RS Triharsi", "Jl. Sabang", "Luwes Kestalan",
        "Pasar Legi Barat", "Pasar Legi", "SMP Widya Wacana", "Kelurahan Stabelan",
        "PDAM Stabelan", "Apotik Widuran", "Pegadaian", "Kejaksaan", "Warung Pelem",
        "Pasar Gede", "Balai Kota", "Benteng Vastenburg", "Telkom",
        "Simpang 3 Lodji Wetan", "Luwes Sangkrah", "BTC Selatan", "Pasar Akik",
        "Alun-Alun Utara", "Polsek Pasar Kliwon", "Pasar Klewer"]),
    ("F8", "bus", "Feeder F8: Sub Terminal Pelangi Mojosongo - Pasar Legi", [
        "Sub Terminal Pelangi Mojosongo", "Sibela Tengah", "Kelurahan Mojosongo",
        "Goa Maria", "Untoroloyo", "Pabrik Jerapah", "Pasar Mojosongo",
        "RS dr. OEN Kandangsapi", "Panggung", "Purbowardayan", "SMAN 1 Surakarta",
        "Margoyudan", "Patung Mayor Achmadi", "SMPN 4 Surakarta", "SMK Kristen 2",
        "Kelurahan Stabelan", "SMP Widya Wacana", "Pasar Legi"]),
    ("F9", "bus", "Feeder F9: Sub Terminal Pelangi Mojosongo - Sub Terminal Semanggi", [
        "Sub Terminal Pelangi Mojosongo", "Pasar Sibela", "Taman Jayawijaya",
        "Jayawijaya Timur", "Jayawijaya Barat", "Simpang Busukan", "Dempo", "Ngaglik",
        "USB Poltekkes", "Patung Banteng Bibis", "SMAN 5 & 6 Surakarta",
        "Masjid Al-Hakam", "Pasar Ngemplak", "Patung Mayor Achmadi",
        "SMPN 4 Surakarta", "SMK Kristen 2", "Kelurahan Stabelan", "SMP Widya Wacana",
        "Pasar Legi", "Pasar Legi Selatan", "Grogolan", "Kelurahan Ketelan",
        "SMA Muhammadiyah 1", "Kantor Kel. Timuran", "Simpang Trisakti",
        "Simpang 3 Notosuman Timur", "Gemblegan", "Simpang Grobakan", "Luwes Gading",
        "Pasar Gading", "Simpang Baturono", "Apil Semanggi", "SPBU Semanggi",
        "Sub Terminal Semanggi"]),
    ("F9", "bus", "Feeder F9 (northbound via Ngarsopuro)", [
        "Simpang 3 Notosuman Timur", "Simpang Notosuman Barat", "Singosaren",
        "Gatot Subroto Ngarsopuro", "Pasar Triwindu Ngarsopuro", "Mangkunegaran",
        "Atria", "Kantor Kel. Timuran"]),
    ("F10", "bus", "Feeder F10: Terminal Palur - Pasar Klewer", [
        "Terminal Palur", "Palur", "Mitra Palur", "ASMI", "Tugu Adipura Jurug",
        "Pasar Pucangsawit", "Boing Tenis Center", "Kantor Kel. Pucangsawit",
        "Pucangsawit Waringin", "Alfamart Jonasan", "Jonasan", "Jagalan Abon Sapi",
        "SMPN 20 Surakarta", "Kantor Kel. Jagalan", "Simpang 3 Wonosaren",
        "SMAN 3 & SMPN 14", "Dr Loo", "SD Warga Surakarta", "Purwodiningratan",
        "Warung Pelem", "Pasar Gede", "Balai Kota", "Benteng Vastenburg", "Telkom",
        "Simpang 3 Lodji Wetan", "Luwes Sangkrah", "BTC Selatan", "Pasar Akik",
        "Alun-Alun Utara", "Polsek Pasar Kliwon", "Pasar Klewer"]),
    ("F12", "bus", "Feeder F12: Pasar Klewer - Lapangan Gentan", [
        "Lapangan Gentan", "Jl. Empu Kanwa", "Kelurahan Gentan", "Luwes Gentan",
        "Jl. Parang Kusumo", "SMPN 9 Surakarta", "Pajang", "Pos Pajang", "Wangkung",
        "Pasar Jongke", "Pusat Oleh-oleh Jongke", "Simpang Batikan", "STMIK Sinus",
        "Al-Muayyad", "SDN Tegalsari", "FKG UMS", "Sutowijoyo", "Penumping",
        "Kelurahan Sriwedari", "GOR Sritex", "Pasar Kadipolo", "SMA Al Islam 1",
        "SMA Kristen 1", "Kantor Kel. Kratonan", "Serengan", "Widya Wacana",
        "SD Kanisius", "SMPN 19 Surakarta", "Sawo Kecik",
        "SMA Islam", "SMKN 3 Surakarta", "Pasar Gading", "Simpang Baturono",
        "Masjid Riyadh", "RS Kustati", "SMPN 6 Surakarta", "SPBU Pasar Kliwon",
        "Kedung Lumbu", "Pasar Klewer"]),
    ("KRL", "rail", "KRL Commuter Line Yogyakarta - Palur (Solo section)", [
        "Purwosari", "Solo Balapan", "Solo Jebres", "Palur"]),
    ("BIAS", "rail", "KA Bandara Adi Soemarmo", [
        "Bandara Adi Soemarmo", "Kadipiro", "Solo Balapan", "Solo Jebres", "Palur"]),
    ("BK", "rail", "KA Batara Kresna (Solo section)", [
        "Purwosari", "Solo Kota"]),
    ("WALK", "walk", "Skybridge Terminal Tirtonadi - Stasiun Solo Balapan", [
        "Terminal Tirtonadi", "Solo Balapan"]),
    ("WALK", "walk", "Interchange walk Jebres bus stop - Stasiun Solo Jebres", [
        "Jebres", "Solo Jebres"]),
    ("WALK", "walk", "Interchange walk Luwes Sangkrah - Stasiun Solo Kota", [
        "Luwes Sangkrah", "Solo Kota"]),
]

# --------------------------------------------------------------------------
# Coordinates. osm_geocoded_stops.csv holds the stops matched automatically to
# OpenStreetMap (Nominatim) features whose name agrees with the stop name and
# that lie on the corridor (see README). OSM_EXTRA holds stops matched by a
# second, hand-checked OpenStreetMap search. All other stops are interpolated.
# --------------------------------------------------------------------------
OSM_EXTRA = {
    # stop on the map: (lat, lon)                       OpenStreetMap feature used
    "Solo Kota": (-7.575690, 110.836260),              # railway station Solo Kota
    "Luwes Sangkrah": (-7.573140, 110.832840),         # bus stop Luwes Sangkrah
    "Jebres": (-7.561800, 110.836100),                 # bus stop Halte Jebres 2
    "Pasar Triwindu Ngarsopuro": (-7.569180, 110.822550),  # marketplace Pasar Triwindu
    "ISI Solo Techno Park": (-7.558040, 110.852460),   # Institut Seni Indonesia Surakarta
    "RS Triharsi": (-7.557360, 110.824780),            # hospital RS Triharsi Surakarta
    "SMAN 3 & SMPN 14": (-7.565350, 110.840960),       # bus stop Halte SMA 3/SMP 14
    "Simpang 3 Gilingan": (-7.553260, 110.823200),     # junction Simpang Tiga Gilingan
    "Garasi BST Tohudan": (-7.532700, 110.768770),     # bus stop Garasi BST
    "Kel. Wirun": (-7.602790, 110.864120),             # bus stop Wirun
    "Coyudan Timur": (-7.574310, 110.822310),          # GKI Coyudan
    "GOR Sritex": (-7.570810, 110.814840),             # Sritex Arena
    "Tyfountex Barat": (-7.563310, 110.761540),        # bus stop Halte Tyfountex Pintu Utama
}


def load_osm_coordinates():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "osm_geocoded_stops.csv")
    coords = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            coords[r["stop_name"]] = (float(r["lat"]), float(r["lon"]))
    coords.update(OSM_EXTRA)
    return coords


INTERCHANGE_TYPES = {
    "Terminal Kartasura": "terminal", "Terminal Palur": "terminal",
    "Terminal Tirtonadi": "terminal", "Sub Terminal Kerten": "sub_terminal",
    "Sub Terminal Pelangi Mojosongo": "sub_terminal",
    "Sub Terminal Semanggi": "sub_terminal", "Bandara Adi Soemarmo": "airport_station",
    "Solo Balapan": "rail_station", "Purwosari": "rail_station",
    "Solo Jebres": "rail_station", "Palur": "rail_station", "Solo Kota": "rail_station",
    "Kadipiro": "rail_station",
}


def haversine_km(a, b):
    """Great-circle distance between two (lat, lon) points in kilometres."""
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(math.sqrt(h))


def assign_coordinates():
    coords = load_osm_coordinates()
    source = {name: "osm" for name in coords}
    # Repeat until every stop is placed: a stop is interpolated between the
    # nearest already-placed stops before and after it in a corridor sequence.
    for _ in range(5):
        for _cid, _mode, _name, seq in CORRIDORS:
            placed = [i for i, s in enumerate(seq) if s in coords]
            for a, b in zip(placed, placed[1:]):
                pa, pb = coords[seq[a]], coords[seq[b]]
                for k in range(a + 1, b):
                    if seq[k] not in coords:
                        t = (k - a) / (b - a)
                        coords[seq[k]] = (round(pa[0] + t * (pb[0] - pa[0]), 6),
                                          round(pa[1] + t * (pb[1] - pa[1]), 6))
                        source[seq[k]] = "interpolated"
    missing = {s for *_r, seq in CORRIDORS for s in seq} - set(coords)
    if missing:
        raise SystemExit(f"Stops without coordinates: {sorted(missing)}")
    return coords, source


def main(out_dir):
    coords, source = assign_coordinates()
    # node ids in order of first appearance
    order = []
    for *_r, seq in CORRIDORS:
        for s in seq:
            if s not in order:
                order.append(s)
    node_id = {s: i + 1 for i, s in enumerate(order)}
    corridors_of = {s: [] for s in order}
    for cid, *_r, seq in CORRIDORS:
        for s in seq:
            if cid not in corridors_of[s]:
                corridors_of[s].append(cid)

    with open(os.path.join(out_dir, "nodes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["node_id", "stop_name", "lat", "lon", "node_type", "corridors",
                    "coord_source"])
        for s in order:
            ntype = INTERCHANGE_TYPES.get(s)
            if ntype is None:
                ntype = "interchange_stop" if len(corridors_of[s]) > 1 else "stop"
            w.writerow([node_id[s], s, f"{coords[s][0]:.6f}", f"{coords[s][1]:.6f}", ntype,
                        "|".join(corridors_of[s]), source[s]])

    edge_rows, seen = [], set()
    for cid, mode, cname, seq in CORRIDORS:
        for u, v in zip(seq, seq[1:]):
            key = (cid, frozenset((u, v)))
            if key in seen:
                continue
            seen.add(key)
            hv = haversine_km(coords[u], coords[v])
            edge_rows.append([node_id[u], node_id[v], u, v, cid, mode,
                              f"{hv:.4f}", f"{FACTOR[mode]:.2f}",
                              f"{hv * FACTOR[mode]:.4f}"])
    with open(os.path.join(out_dir, "edges.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["edge_id", "from_id", "to_id", "from_stop", "to_stop", "corridor",
                    "mode", "haversine_km", "circuity_factor", "distance_km"])
        for i, row in enumerate(edge_rows, 1):
            w.writerow([i] + row)
    print(f"nodes: {len(order)}  edges: {len(edge_rows)}  "
          f"osm: {sum(1 for s in order if source[s] == 'osm')}  "
          f"interpolated: {sum(1 for s in order if source[s] == 'interpolated')}")


if __name__ == "__main__":
    main(os.path.dirname(os.path.abspath(__file__)))
