"""Road distance (miles) and drive time (hours) from each candidate metro's population centre to every contiguous-US
county centre of population, using the public OSRM demo server (OpenStreetMap). One request per second; resumable."""
import pandas as pd, json, time, subprocess, os
metros = pd.read_csv('raw/metro_centers.csv', dtype={'CBSA': str})
cty = pd.read_csv('raw/county_food_demand.csv', dtype={'GEOID': str})
os.makedirs('raw/osrm', exist_ok=True)
B = 99
for _, m in metros.iterrows():
    f = f'raw/osrm/{m.CBSA}.csv'
    if os.path.exists(f): continue
    rows = []
    for i in range(0, len(cty), B):
        part = cty.iloc[i:i + B]
        coords = f'{m.lon:.6f},{m.lat:.6f};' + ';'.join(f'{a:.6f},{b:.6f}' for a, b in zip(part.lon, part.lat))
        url = f'https://router.project-osrm.org/table/v1/driving/{coords}?sources=0&annotations=distance,duration'
        for attempt in range(5):
            try:
                # curl instead of urllib: the local Python's SSL library fails the TLS handshake with this server
                out = subprocess.run(['curl', '-s', '--max-time', '60', '-A', 'research-script', url],
                                     capture_output=True, text=True, check=True).stdout
                r = json.loads(out)
                if r.get('code') != 'Ok': raise ValueError(r.get('code'))
                break
            except Exception as e:
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f'failed {m.CBSA} batch {i}')
        d, t = r['distances'][0][1:], r['durations'][0][1:]
        for g, dd, tt, snap in zip(part.GEOID, d, t, r['destinations'][1:]):
            rows.append({'CBSA': m.CBSA, 'GEOID': g, 'road_miles': None if dd is None else dd / 1609.344,
                         'drive_hours': None if tt is None else tt / 3600, 'snap_m': snap.get('distance')})
        time.sleep(1)
    pd.DataFrame(rows).to_csv(f, index=False); print('done', m.Metro, flush=True)
print('all done')
