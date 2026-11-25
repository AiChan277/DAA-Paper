# Saran Tulis Ulang — Paper BFS/DFS/B&B Surakarta

Basis: hasil GPTZero (Advanced Scan, 100% AI) + pola gaya yang biasa memicu detektor.
Ejaan: British English (sudah konsisten: *-ise, neighbouring, kilometres*), gaya IEEE.

**Aturan main**
- Teks `[DALAM KURUNG SIKU]` = isi dengan fakta/alasanmu sendiri. Jangan diisi karangan.
- Contoh tulisan di bawah hanya arah, bukan untuk ditempel. Tulis ulang dengan kalimatmu sendiri.
- Hindari em dash (—) di versi barumu; pakai koma atau kurung. Em dash juga termasuk ciri yang sering dianggap "AI".

---

## A. Prioritas tinggi (ditandai GPTZero)

### A1. Related Work, paragraf 2 — Prasetyo et al. [7] — **High AI impact**
**Asli:**
> Prasetyo et al. [7] ran both algorithms on an unweighted road graph of Kaliuntu, Bali, with 15 nodes and 20 edges stored as an adjacency list; BFS was faster and more stable (0.082 ms against 0.158 ms) while DFS produced more distinct routes (9 against 6).

**Masalah:** satu kalimat memuat setting, struktur data, dua perbandingan, dua kurung angka. Sangat padat dan simetris (*X was …, while Y …*).

**Arah tulis ulang:** pecah jadi 2–3 kalimat, satu ide per kalimat.
> Prasetyo et al. [7] tested both algorithms on a small unweighted road graph of Kaliuntu, Bali (15 nodes, 20 edges). BFS was the faster of the two, at 0.082 ms against 0.158 ms, and its run times varied less. DFS, however, found nine distinct routes where BFS found six.

### A2. Introduction, paragraf 1 — "Previous work on the BST network…" — Medium
**Asli:**
> Previous work on the BST network has measured its spatial coverage, showing that a 400 m service area around existing stops reaches 126 elementary schools and 43 urban villages [1], but has not examined how passengers find a route through the network once they are on it.

**Masalah:** pola "has X, showing Y, but has not Z" — rapi tapi generik. Sebutkan penulisnya.

**Arah:**
> Earlier work on BST has focused on coverage. Syaharini et al. [1] showed that a 400 m service area around the existing stops reaches 126 elementary schools and 43 urban villages. How a passenger then chooses a route through the network was outside the scope of that study.

### A3. Introduction, paragraf 2 — "One hop can therefore mean…" — Medium
**Asli:**
> One hop can therefore mean a short ride between neighbouring stops or a long train journey, and a route that is minimal in hops is not necessarily minimal in kilometres travelled.

**Masalah:** kalimat penutup yang "merangkum" kalimat sebelumnya; *therefore* + *not necessarily*. Kalimat sebelumnya sudah punya angka konkret, jadi ini terasa mengulang.

**Arah:** ganti kesimpulan abstrak dengan konsekuensi konkret dari datamu.
> To a hop-counting search, the 60 m step between Widya Wacana and SD Kanisius and the 8.62 km run to the airport cost exactly the same.

(Lalu hapus klausa "a route that is minimal in hops …", karena Results sudah membuktikannya.)

### A4. Dataset — "Stop coordinates were obtained by geocoding…" — Medium
**Asli:**
> Stop coordinates were obtained by geocoding every stop name with OpenStreetMap (Nominatim) inside the Surakarta metropolitan area.

**Masalah:** pasif, generik, tidak ada jejak "apa yang benar-benar kamu alami".

**Arah:** ceritakan prosesnya dan satu kendala nyata.
> Each stop name was queried in OpenStreetMap through Nominatim, with the search restricted to the Surakarta metropolitan area. [CONTOH KENDALA: misalnya nama halte yang muncul di dua tempat / hasil yang jatuh di kota lain, dan bagaimana kamu menanganinya.]

### A5. Dataset — "The remaining 69 stops…" — Medium
**Asli:**
> The remaining 69 stops, mostly small kerbside stops without a mapped landmark, were placed by linear interpolation between their geocoded neighbours along the corridor.

**Arah:** tambahkan alasan/dampak yang hanya kamu tahu.
> The other 69 stops could not be matched, mostly because they are kerbside signs with no landmark in OpenStreetMap. [ALASAN memilih interpolasi linear, mis. jarak antarhalte di koridor yang sama relatif seragam / tidak ada sumber koordinat lain.] Their positions were interpolated linearly between the nearest geocoded stops on the same corridor, [PERKIRAAN GALAT jika ada, mis. "which we expect to be within … m"].

---

## B. Prioritas sedang (pola yang biasa memicu detektor)

### B1. Introduction — kalimat pendek "pembuka dramatis"
- *"Route finding is naturally a graph problem."*
- *"This study addresses that gap."*

**Masalah:** kalimat pendek bergaya punchline lalu dijelaskan; pola klasik tulisan AI.

**Arah:** gabungkan ke kalimat berikutnya.
> In the L-space representation commonly used for transit networks, each stop is a vertex and consecutive stops on a corridor share an edge [2].

> The objectives of this study are to (i) …

### B2. Method — faktor sirkuitas 1.20 / 1.10 / 1.30
> … 1.20 for road corridors (the urban road factor), 1.10 for rail and 1.30 for the walking link …

**Masalah:** bukan soal detektor saja; reviewer akan bertanya "dari mana angka ini?". Menambahkan alasan juga membuat bagian ini jelas tulisan manusia.

**Arah:** tambahkan satu kalimat.
> [SUMBER atau CARA kamu menentukan angka: sitasi literatur circuity, atau "checked against the road distance of N sample segments, which gave a mean ratio of …".]

### B3. Results 4.1 — "The cause is structural:" + "shows the effect clearly."
**Asli:**
> The cause is structural: rail edges are 3.3–5.1 km long on average (Table 1), against 0.40 km for bus edges, but count as a single hop, so BFS uses rail in ten of the 15 routes, whereas the distance-optimal B&B route uses rail in two (M3 and L2). Scenario S5 (Kleco to Gladag) shows the effect clearly.

**Masalah:** pembuka + titik dua dramatis; *so … whereas …* dalam satu kalimat; "shows the effect clearly".

**Arah:**
> This happens because rail edges average 3.3 to 5.1 km (Table 1), compared with 0.40 km for bus edges, yet each still counts as one hop. BFS used rail in ten of the 15 routes; the distance-optimal B&B route used it in only two (M3 and L2). In S5 (Kleco to Gladag), for instance, …

### B4. Results 4.1 — penutup paragraf DFS
**Asli:**
> In a graph of interlocking corridor loops, the first path that DFS finds is determined by which neighbour happens to be listed first, not by its cost.

**Masalah:** kalimat penutup bergaya aforisme ("X, not Y").

**Arah:** ganti dengan observasi konkret dari datamu, atau hapus (kalimat sebelumnya sudah cukup).
> [CONTOH: koridor/loop mana yang membuat DFS "nyasar" di L3, mis. "On L3, DFS first entered the … loop and only reached Simpang Sidan after …".]

### B5. Results 4.2 — "Execution time ranks the algorithms differently."
**Arah:** gabung dengan angka langsung.
> In execution time the order was reversed: BFS was fastest (30.1 µs per query on average), followed by DFS (49.3 µs), Dijkstra (102.1 µs) and B&B (166.0 µs).

### B6. Discussion — "They add a finding that small, single-mode graphs do not reveal:"
**Arah:** lebih datar, tanpa titik dua dramatis.
> What the earlier studies could not show, because their graphs were small and single-mode, is how far the two objectives drift apart when stop spacing varies.

### B7. Conclusion — mengulang abstrak
Kesimpulan memuat hampir semua angka yang sama dengan abstrak (9.03 km, 1.3 transfers, 53.4%, 30.1 µs, 35.2%, 45.09 km, 20%, 1.5%). Detektor dan reviewer sama-sama tidak suka ini.

**Arah:** sisakan 2–3 angka kunci, sisanya ganti dengan makna/rekomendasi praktis dari sudut pandangmu.
> [MISAL: siapa yang akan memakai hasil ini (aplikasi BST? Dishub?) dan apa yang paling penting bagi mereka.]

---

## C. Pola yang diulang di seluruh teks

| Pola | Jumlah | Saran |
|---|---|---|
| `, which …` | 7 | sisakan ±3, sisanya pecah jadi kalimat baru |
| titik koma `;` | 17 | sisakan ±6; titik koma beruntun bikin ritme seragam |
| *therefore* | 5 | sisakan 1–2; ganti dengan *so*, *as a result*, atau hapus |
| *whereas* | 4 | sisakan 1; pakai *while*, *but*, atau dua kalimat |
| *so that* | 4 | sisakan 1–2 |
| *for example* / *for instance* | 5 | sisakan 2 |
| Pembuka pendek + titik dua (`The cause is structural:`) | beberapa | ganti dengan kalimat biasa |

**Tips ritme:** campur kalimat 8–12 kata dengan kalimat 25–30 kata. Yang paling dicurigai detektor adalah paragraf yang semua kalimatnya 25–35 kata dengan struktur sama.

---

## D. Setelah menulis ulang
1. Scan ulang **per bagian** (mis. Method saja), bukan seluruh paper. Advanced Scan gratismu sudah habis; Basic Scan masih bisa dipakai dan kreditmu tersisa sekitar 8.400 kata bulan ini.
2. Jangan memakai paraphraser otomatis, karena hasilnya sering tetap ditandai dan bisa merusak istilah teknis.
3. Simpan draf lama + hasil scan sebagai bukti proses.
