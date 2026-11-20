# Geocodes every stop name with OpenStreetMap Nominatim (1 request per second,
# results limited to the Surakarta metropolitan bounding box).
$ErrorActionPreference = 'Continue'
$out = 'D:\Paper\DAA\_osm\geocode_results.jsonl'
if (Test-Path $out) { Remove-Item $out }
$headers = @{ 'User-Agent' = 'UNS-DAA-student-project-surakarta-transit/1.0 (coursework)'; 'Accept-Language' = 'id,en' }
$lines = Get-Content 'D:\Paper\DAA\_osm\stops.txt' -Encoding UTF8
foreach ($line in $lines) {
  $p = $line -split "`t"
  $id = $p[0]; $name = $p[1]
  foreach ($q in @($p[2], $p[3])) {
    $url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&bounded=1&viewbox=110.70,-7.50,110.93,-7.63&countrycodes=id&q=' + [uri]::EscapeDataString($q)
    try {
      $r = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 30
      foreach ($x in $r) {
        $o = [ordered]@{ id = $id; stop = $name; query = $q; osm_name = $x.name; display = $x.display_name; lat = $x.lat; lon = $x.lon; category = $x.category; type = $x.type }
        Add-Content -Path $out -Value ($o | ConvertTo-Json -Compress) -Encoding UTF8
      }
      if (-not $r) { Add-Content -Path $out -Value (([ordered]@{ id = $id; stop = $name; query = $q; none = $true }) | ConvertTo-Json -Compress) -Encoding UTF8 }
    } catch {
      Add-Content -Path $out -Value (([ordered]@{ id = $id; stop = $name; query = $q; error = $_.Exception.Message }) | ConvertTo-Json -Compress) -Encoding UTF8
    }
    Start-Sleep -Milliseconds 1100
  }
  Write-Output "$id $name"
}
Write-Output 'DONE'
