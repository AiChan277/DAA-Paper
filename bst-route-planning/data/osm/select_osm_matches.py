"""
select_osm_matches.py
---------------------
Chooses, for every stop, the OpenStreetMap feature returned by Nominatim
(raw/*.jsonl, produced by geocode_nominatim.ps1) that best matches the stop:
the feature name must contain the stop name (abbreviations such as SMPN or RS
expanded), the feature must be a bus stop, station or named landmark (not a
village area or a street), and it must lie within 3.5 km of the stop's rough
position (prior_estimates.csv). Hand-checked rejections are listed in
FORCE_REJECT. Writes ../osm_geocoded_stops.csv, which build_dataset.py reads.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
import json,glob,csv,math,re
recs=[]
for f in glob.glob(os.path.join(HERE, 'raw', '*.jsonl')):
    for l in open(f,encoding='utf-8-sig'):
        l=l.strip().lstrip('﻿')
        if l:
            try: recs.append(json.loads(l))
            except: pass
N={n['node_id']:n for n in csv.DictReader(open(os.path.join(HERE, '..', 'nodes.csv'), encoding='utf-8'))}
def hv(a,b,c,d):
    p1,p2=math.radians(a),math.radians(c); dp=p2-p1; dl=math.radians(d-b)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*6371*math.asin(math.sqrt(h))
STOP=set('halte bst di jalan jl kota surakarta solo the'.split())
def norm(s):
    s=s.lower()
    rep=[(r'\bsmpn\b','smp negeri'),(r'\bsman\b','sma negeri'),(r'\bsmkn\b','smk negeri'),(r'\bsdn\b','sd negeri'),
         (r'\brsud\b','rsud'),(r'\brs\b','rumah sakit'),(r'\bkel\.?\b','kelurahan'),(r'\bkec\.?\b','kecamatan'),
         (r'\bmuh\b','muhammadiyah'),(r'\bst\.?\b','stasiun'),(r'\bstasiun\b','stasiun'),(r'\bnegri\b','negeri')]
    for a,b in rep: s=re.sub(a,b,s)
    s=re.sub(r'[^a-z0-9 ]',' ',s)
    return [t for t in s.split() if t not in STOP]
recs=[]
for f in glob.glob(os.path.join(HERE, 'raw', '*.jsonl')):
    for l in open(f,encoding='utf-8-sig'):
        l=l.strip().lstrip('﻿')
        if l:
            try: recs.append(json.loads(l))
            except: pass
GOOD_CAT={'railway','public_transport','amenity','shop','tourism','office','historic','junction','aeroway','building','military'}
def ok_type(c, stop):
    cat,typ=c['category'],c['type']
    if cat=='highway':
        if typ in ('bus_stop','platform','traffic_signals','stop'): return True
        if typ=='service' and 'terminal' in (c.get('osm_name') or '').lower(): return True
        return False
    if cat=='leisure': return typ in ('park','pitch','stadium','sports_centre')
    if cat=='landuse': return stop.lower().startswith('lapangan')
    return cat in GOOD_CAT
WHITELIST={'Gajahan IHS','Gedung Wanita / SMPN 1 Surakarta','Pasar Pucangsawit','Pos Pajang','Kelurahan Sriwedari','Lotte Grosir Tipes'}
FORCE_REJECT={'Sriwedari 1':['Ayam'],'UMS':['Danau','Lapangan','FKG'],'UNS':['Danau','Taman','Universitas'],'SPBU Colomadu':None,'Malangjiwan Utara':None,'Banyuagung':None,'Jonasan':['Alfamart'],'Pasar Gede':['Pasar Akik'],'FKG UMS':['Halte'],'Pegadaian':None,'PKU Kartasura':None}
PRIOR={r['stop_name']:(float(r['lat']),float(r['lon'])) for r in csv.DictReader(open(os.path.join(HERE, 'prior_estimates.csv'), encoding='utf-8'))}
PRIOR['Jebres']=PRIOR['Solo Jebres']; PRIOR['Luwes Sangkrah']=PRIOR['Solo Kota']
cands={}
for r in recs:
    if r.get('lat') and 'stop' in r: cands.setdefault(r['stop'],[]).append(r)
chosen={}
for i,n in N.items():
    st=norm(n['stop_name']); plat,plon=PRIOR[n['stop_name']]
    best=None
    for c in cands.get(n['stop_name'],[]):
        if not ok_type(c,n['stop_name']): continue
        nm=(c.get('osm_name') or '')
        fr=FORCE_REJECT.get(n['stop_name'],'-')
        if fr!='-' and (fr is None or any(x.lower() in nm.lower() for x in fr)): continue
        ot=set(norm(nm)); cover=len(set(st)&ot)/max(1,len(set(st)))
        if cover<0.99 and n['stop_name'] not in WHITELIST: continue
        if cover<0.4: continue
        d=hv(plat,plon,float(c['lat']),float(c['lon']))
        if d>3.5: continue
        score=cover+(0.3 if c['type']=='bus_stop' or c['category'] in ('railway','public_transport') else 0)-0.1*d
        if best is None or score>best[0]: best=(score,c,d)
    if best: chosen[i]=best
# manual reassignment: OSM "SD 3 Banyuagung" bus stop belongs to stop 214 (SDN 3 Banyuagung)
for c in cands.get('Banyuagung',[]):
    sid=[k for k,v in N.items() if v['stop_name']=='SDN 3 Banyuagung'][0]
    if 'SD 3 Banyuagung' in (c.get('osm_name') or '') and sid not in chosen:
        chosen[sid]=(1.0,c,0)
with open(os.path.join(HERE, '..', 'osm_geocoded_stops.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['node_id','stop_name','lat','lon','osm_name','osm_type','shift_km'])
    for i,n in N.items():
        if i in chosen:
            s,c,d=chosen[i]
            w.writerow([i,n['stop_name'],f"{float(c['lat']):.6f}",f"{float(c['lon']):.6f}",c.get('osm_name'),f"{c['category']}/{c['type']}",f"{d:.2f}"])
print('geocoded',len(chosen),'of',len(N))
print('missing:',[N[i]['stop_name'] for i in N if i not in chosen])
