[System.Net.WebRequest]::DefaultWebProxy = $null
$out = '.\hubs.jsonl'
if (Test-Path $out) { Remove-Item $out }
$headers = @{ 'User-Agent' = 'UNS-DAA-student-project-surakarta-transit/1.0 (coursework)' }
$qs = @('Stasiun Solo Kota','Solo Kota','Sangkrah','Pasar Gede Hardjonagoro','Pasar Gede','Pasar Triwindu','Rumah Sakit Dr. Oen Kandang Sapi','Dr. Oen','Institut Seni Indonesia Surakarta','ISI Surakarta','Monumen Mayor Achmadi','Patung Mayor Achmadi','Gatot Subroto','Kimia Farma','RS Triharsi','Rumah Sakit Triharsi','SMA Negeri 5 Surakarta','SMA Negeri 6 Surakarta','Halte Kemlayan','Halte Penumping','GOR Sritex','Sritex Arena','Simpang Batikan','SMA Muhammadiyah 2 Surakarta','SMA Muhammadiyah 3 Surakarta','STMIK Sinus','Tyfountex','Superindo Gumpang','Jalan Dokter Radjiman','Coyudan','SMP Negeri 6 Surakarta','Halte Serengan','Kantor Kelurahan Timuran','Simpang Trisakti','SMA Negeri 3 Surakarta','Halte Jajar','Sekolah Ursulin','SMK Negeri 5 Surakarta','Simpang Tiga Gilingan','Garasi BST','Halte Klodran','Halte Gedongan','Wirun','Halte Pajang','Halte Kedung Lumbu','Halte Grogolan','Halte Purwodiningratan','Luwes Sangkrah')
foreach ($q in $qs) {
  $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&bounded=1&viewbox=110.70,-7.50,110.93,-7.63&countrycodes=id&q=' + [uri]::EscapeDataString($q)
  try { $r = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 30 } catch { $r = $null }
  foreach ($x in $r) { Add-Content -Path $out -Value (([ordered]@{ query = $q; osm_name = $x.name; lat = $x.lat; lon = $x.lon; category = $x.category; type = $x.type }) | ConvertTo-Json -Compress) -Encoding UTF8 }
  Start-Sleep -Milliseconds 1200
}
Add-Content -Path $out -Value '{"done":true}' -Encoding UTF8
'DONE'
