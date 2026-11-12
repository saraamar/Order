"""Allocate 2022 CFS food truck tonnage (SCTG 05-09, domestic, truck modes) from CFS destination areas to counties
in proportion to 2020 county population. Run from the site_data folder."""
import pandas as pd
lk = pd.read_excel('raw/list2022.xlsx', sheet_name='CFSAreas', dtype=str)
lk['GEOID'] = lk.ST.str.zfill(2) + lk.CNTY.str.zfill(3)
lk['DEST_CFS_AREA'] = lk.ST.str.zfill(2) + '-' + lk.CFS22_AREA.str.strip()
cp = pd.read_csv('raw/CenPop2020_Mean_CO.txt', dtype={'STATEFP': str, 'COUNTYFP': str}, encoding='utf-8-sig')
cp['GEOID'] = cp.STATEFP + cp.COUNTYFP
cp = cp[~cp.STATEFP.isin(['02', '15', '72'])]                      # contiguous US only
m = cp.merge(lk[['GEOID', 'DEST_CFS_AREA', 'CFS22_NAME']], on='GEOID', how='left')
print('counties:', len(m), '| unmatched to a CFS area:', m.DEST_CFS_AREA.isna().sum())
print(m[m.DEST_CFS_AREA.isna()][['GEOID', 'COUNAME', 'STNAME']].to_string(index=False))
t = pd.read_csv('raw/cfs2022_truck_domestic_by_sctg_dest.csv', dtype=str)
t['tons'] = t.tons.astype(float); t['n'] = t.n.astype(float)
food = t[t.SCTG.isin(['05', '06', '07', '08', '09', '06-09'])].groupby('DEST_CFS_AREA').agg(food_tons=('tons', 'sum'), cfs_records=('n', 'sum')).reset_index()
m['area_pop'] = m.groupby('DEST_CFS_AREA').POPULATION.transform('sum')
m = m.merge(food, on='DEST_CFS_AREA', how='left')
m['food_tons_2022'] = m.food_tons * m.POPULATION / m.area_pop
areas_no_county = sorted(set(food.DEST_CFS_AREA) - set(m.DEST_CFS_AREA))
print('CFS areas with tonnage but no contiguous county:', areas_no_county,
      round(food[food.DEST_CFS_AREA.isin(areas_no_county)].food_tons.sum() / 1e6, 2), 'M tons')
print('Allocated M tons:', round(m.food_tons_2022.sum() / 1e6, 1), 'of', round(food.food_tons.sum() / 1e6, 1))
out = m[['GEOID', 'COUNAME', 'STNAME', 'POPULATION', 'LATITUDE', 'LONGITUDE', 'DEST_CFS_AREA', 'CFS22_NAME',
         'area_pop', 'food_tons', 'cfs_records', 'food_tons_2022']].rename(columns={
    'COUNAME': 'county', 'STNAME': 'state', 'POPULATION': 'pop_2020', 'LATITUDE': 'lat', 'LONGITUDE': 'lon',
    'DEST_CFS_AREA': 'cfs_area', 'CFS22_NAME': 'cfs_area_name', 'area_pop': 'cfs_area_pop_2020',
    'food_tons': 'cfs_area_food_tons', 'cfs_records': 'cfs_area_records', 'food_tons_2022': 'county_food_tons_2022'})
out.to_csv('raw/county_food_demand.csv', index=False)
print(out.sort_values('county_food_tons_2022', ascending=False).head(8)[['county', 'state', 'pop_2020', 'cfs_area', 'county_food_tons_2022']].to_string(index=False))
