param([int]$Worker = 0, [int]$Workers = 4)
# Geocodes stop names with OpenStreetMap Nominatim inside the Surakarta bounding box.
# Each worker handles every n-th stop and waits 4 s between requests, so all
# workers together stay below Nominatim's limit of 1 request per second.
[System.Net.WebRequest]::DefaultWebProxy = $null
$out = "D:\Paper\DAA\_osm\geo_w$Worker.jsonl"
$headers = @{ 'User-Agent' = 'UNS-DAA-student-project-surakarta-transit/1.0 (coursework)'; 'Accept-Language' = 'id,en' }
$done = @{}
if (Test-Path 'D:\Paper\DAA\_osm\geocode_results.jsonl') {
  Get-Content 'D:\Paper\DAA\_osm\geocode_results.jsonl' -Encoding UTF8 | ForEach-Object { try { $done[($_ | ConvertFrom-Json).id] = 1 } catch {} }
}
$lines = Get-Content 'D:\Paper\DAA\_osm\stops.txt' -Encoding UTF8
$k = 0
foreach ($line in $lines) {
  $k++
  if (($k % $Workers) -ne $Worker) { continue }
  $p = $line -split "`t"
  $id = $p[0]; $name = $p[1]
  if ($done.ContainsKey($id)) { continue }
  foreach ($q in @($p[2], $p[3], $name) | Select-Object -Unique) {
    $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&bounded=1&viewbox=110.70,-7.50,110.93,-7.63&countrycodes=id&q=' + [uri]::EscapeDataString($q)
    $r = $null
    try { $r = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 30 } catch {
      Add-Content -Path $out -Value (([ordered]@{ id = $id; stop = $name; query = $q; error = $_.Exception.Message }) | ConvertTo-Json -Compress) -Encoding UTF8
    }
    Start-Sleep -Milliseconds 4000
    if ($r) {
      foreach ($x in $r) {
        $o = [ordered]@{ id = $id; stop = $name; query = $q; osm_name = $x.name; display = $x.display_name; lat = $x.lat; lon = $x.lon; category = $x.category; type = $x.type }
        Add-Content -Path $out -Value ($o | ConvertTo-Json -Compress) -Encoding UTF8
      }
      break
    }
  }
  Add-Content -Path $out -Value (([ordered]@{ id = $id; stop = $name; finished = $true }) | ConvertTo-Json -Compress) -Encoding UTF8
}
Add-Content -Path $out -Value '{"worker_done":true}' -Encoding UTF8
