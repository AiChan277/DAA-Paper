param([int]$Worker = 0, [int]$Workers = 4)
# Second pass: retries stops that failed or matched poorly (stops_retry.txt).
[System.Net.WebRequest]::DefaultWebProxy = $null
$out = "D:\Paper\DAA\_osm\retry_w$Worker.jsonl"
if (Test-Path $out) { Remove-Item $out }
$headers = @{ 'User-Agent' = 'UNS-DAA-student-project-surakarta-transit/1.0 (coursework)'; 'Accept-Language' = 'id,en' }
$lines = Get-Content 'D:\Paper\DAA\_osm\stops_retry.txt' -Encoding UTF8
$k = 0
foreach ($line in $lines) {
  $k++
  if (($k % $Workers) -ne $Worker) { continue }
  $p = $line -split "`t"
  $id = $p[0]; $name = $p[1]
  foreach ($q in @($p[2], $p[3]) | Select-Object -Unique) {
    $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&bounded=1&viewbox=110.70,-7.50,110.93,-7.63&countrycodes=id&q=' + [uri]::EscapeDataString($q)
    $r = $null
    for ($try = 0; $try -lt 3 -and -not $r; $try++) {
      try { $r = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 30; if (-not $r) { $r = @() ; break } } catch { Start-Sleep -Seconds 5 }
    }
    Start-Sleep -Milliseconds 4000
    foreach ($x in $r) {
      $o = [ordered]@{ id = $id; stop = $name; query = $q; osm_name = $x.name; display = $x.display_name; lat = $x.lat; lon = $x.lon; category = $x.category; type = $x.type }
      Add-Content -Path $out -Value ($o | ConvertTo-Json -Compress) -Encoding UTF8
    }
  }
  Add-Content -Path $out -Value (([ordered]@{ id = $id; stop = $name; finished = $true }) | ConvertTo-Json -Compress) -Encoding UTF8
}
Add-Content -Path $out -Value '{"worker_done":true}' -Encoding UTF8
