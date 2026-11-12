"""Turn metro-to-county road distances into demand criteria and add them to the workbook."""
import pandas as pd, glob
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

cty = pd.read_csv('raw/county_food_demand.csv', dtype={'GEOID': str})
dist = pd.concat(pd.read_csv(f, dtype={'CBSA': str, 'GEOID': str}) for f in glob.glob('raw/osrm/*.csv'))
d = dist.merge(cty[['GEOID', 'pop_2020', 'county_food_tons_2022']], on='GEOID')
US_TONS = cty.county_food_tons_2022.sum()

def summ(g):
    ok = g.road_miles.notna()
    w250, w500 = ok & (g.road_miles <= 250), ok & (g.road_miles <= 500)
    near = g[w500]
    return pd.Series({
        'C7 Food demand within 250 road miles (M tons/yr)': g.loc[w250, 'county_food_tons_2022'].sum() / 1e6,
        'Share of U.S. food demand within 250 mi (%)': 100 * g.loc[w250, 'county_food_tons_2022'].sum() / US_TONS,
        'Food demand within 500 road miles (M tons/yr)': g.loc[w500, 'county_food_tons_2022'].sum() / 1e6,
        'Population within 250 road miles (M)': g.loc[w250, 'pop_2020'].sum() / 1e6,
        'C8 Demand-weighted mean road miles to demand within 500 mi': (near.road_miles * near.county_food_tons_2022).sum() / near.county_food_tons_2022.sum(),
        'Counties within 250 mi': int(w250.sum()),
        'Unroutable counties': int((~ok).sum())})

cov = d.groupby('CBSA').apply(summ, include_groups=False).reset_index().round(2)
cov.to_csv('raw/demand_coverage.csv', index=False)

F = 'Paper1_Site_Criteria_Data.xlsx'
sheets = pd.read_excel(F, sheet_name=None, dtype={'CBSA': str})
main = sheets['Criteria by metro'].drop(columns=[c for c in sheets['Criteria by metro'].columns if c in cov.columns and c != 'CBSA'])
sheets['Criteria by metro'] = main.merge(cov.drop(columns=['Unroutable counties']), on='CBSA', how='left')
defs = sheets['Criteria definitions']
defs = defs[defs.Code != 'Pending']
new = pd.DataFrame([
    ['C7', 'Market access: food demand within 250 road miles of the metro centre', 'million tons/yr', 'Benefit: higher is better',
     '2022 CFS PUMS, SCTG 05-09, domestic truck shipments (modes 111-113), weighted; CFS destination-area tons allocated to counties by 2020 population; road miles by OSRM (OpenStreetMap) from metro population centre to county centre of population',
     '2022 flows; 2020 population', 'https://www.census.gov/data/datasets/2022/econ/cfs/historical-datasets.html',
     'Metro centre = population-weighted mean of 2020 county centres of population (2023 CBSA delineation). Contiguous US counties only (3,108).'],
    ['C8', 'Service distance: demand-weighted mean road miles to food demand within 500 miles', 'miles', 'Cost: lower is better',
     'Same as C7', '2022 flows; 2020 population', 'https://project-osrm.org/', 'Optional alternative to C7; choose one.'],
], columns=defs.columns)
sheets['Criteria definitions'] = pd.concat([defs, new], ignore_index=True)
with pd.ExcelWriter(F, engine='openpyxl') as w:
    for k, v in sheets.items(): v.to_excel(w, sheet_name=k, index=False)
wb = load_workbook(F)
for ws in wb:
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F4E79')
        c.alignment = Alignment(wrap_text=True, vertical='top')
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = min(60, max(12, max(len(str(c.value or '')) for c in col[:25]) * 0.9))
    if ws.title in ('Criteria definitions', 'Candidate rule', 'Excluded metros'):
        for row in ws.iter_rows(min_row=2):
            for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'C2' if ws.title in ('Criteria by metro', 'All 20 (reference)') else 'A2'
wb.save(F)
print(sheets['Criteria by metro'][['Metro'] + list(cov.columns[1:-1])].to_string(index=False))
print('unroutable:', cov['Unroutable counties'].tolist())
