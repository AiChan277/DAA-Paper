$q = @"
[out:json][timeout:240];
(
  nwr["name"]["highway"="bus_stop"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["public_transport"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["railway"~"station|halt|stop"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["amenity"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["shop"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["leisure"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["tourism"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["office"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["historic"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["place"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["aeroway"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["building"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["landuse"](-7.625,110.72,-7.505,110.92);
  nwr["name"]["military"](-7.625,110.72,-7.505,110.92);
  way["name"]["highway"](-7.625,110.72,-7.505,110.92);
  way["name"]["bridge"](-7.625,110.72,-7.505,110.92);
);
out center tags;
"@
Invoke-WebRequest -Uri 'https://overpass-api.de/api/interpreter' -Method Post -Body @{data=$q} -OutFile 'D:\Paper\DAA\_osm\osm_solo.json' -TimeoutSec 300 -UseBasicParsing
(Get-Item 'D:\Paper\DAA\_osm\osm_solo.json').Length
