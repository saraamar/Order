"""Build Paper1_Site_Criteria_Data.xlsx (all 20 metros) from raw/site_criteria.csv; restrict16.py then narrows it to 16."""
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
df = pd.read_csv('raw/site_criteria.csv', dtype={'CBSA': str})
defs = pd.DataFrame([
 ['C1', 'Warehouse/distribution asking rent', '$/sq ft/yr (net)', 'Cost: lower is better', 'Cushman & Wakefield, U.S. Industrial MarketBeat Q3 2026 (preliminary), "Asking rents" table, W/D column', 'Q3 2026', 'https://assets.cushmanwakefield.com/-/media/cw/marketbeat-pdfs/2026/q3/us-reports/national/q32026usindustrialmarketbeat.pdf', 'Covers 16 of 20 metros.'],
 ['C2', 'Labor cost: mean hourly wage, SOC 53-7062 (hand laborers & freight, stock and material movers)', '$/hour', 'Cost: lower is better', 'BLS OEWS metro estimates via BLS Public Data API (series OEUM00<CBSA>000000537062 03)', 'May 2025', 'https://www.bls.gov/oes/', 'Latest OEWS release.'],
 ['C3', 'Labor availability: employment in SOC 53-7062', 'jobs', 'Benefit: higher is better', 'BLS OEWS (series ... 01); per-1,000-jobs from series ... 16', 'May 2025', 'https://www.bls.gov/oes/', 'Size of the existing warehouse workforce.'],
 ['C4', 'Labor availability: unemployment rate', '%', 'Benefit: higher means more slack (direction is a modelling choice)', 'BLS LAUS metro, not seasonally adjusted (series LAUMT<state><CBSA>00000003); labor force from ...06', '12-month average, Oct 2025 to Sep 2026', 'https://www.bls.gov/lau/', '11 months: Oct 2025 not published (2025 lapse in appropriations).'],
 ['C5', 'Interstate access: interstate centerline miles inside the metro', 'miles', 'Benefit: higher is better', 'BTS NTAD National Highway System (SIGNT1 = I), clipped to 2023 Census CBSA boundaries, measured in EPSG:5070', 'NHS current release', 'https://geodata.bts.gov/', 'Includes 3-digit spurs and loops.'],
 ['C6', 'Interstate access: number of 2-digit mainline interstates with at least 1 mile inside the metro', 'count', 'Benefit: higher is better', 'Same as C5', 'NHS current release', '', 'Alternative to C5; choose one.'],
 ['Extra', 'Industrial vacancy rate', '%', 'Optional: space availability', 'Cushman & Wakefield MarketBeat Q3 2026', 'Q3 2026', '', ''],
 ['Extra', 'Population', 'persons', 'Context / candidate rule', 'Census Bureau CBSA population estimates (Vintage 2024)', 'July 1, 2024', 'https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/metro/totals/', ''],
], columns=['Code', 'Criterion', 'Unit', 'Direction', 'Source', 'Reference period', 'URL', 'Notes'])
with pd.ExcelWriter('Paper1_Site_Criteria_Data.xlsx', engine='openpyxl') as w:
    df.to_excel(w, sheet_name='Criteria by metro', index=False); defs.to_excel(w, sheet_name='Criteria definitions', index=False)
wb = load_workbook('Paper1_Site_Criteria_Data.xlsx')
for ws in wb:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F4E79'); c.alignment = Alignment(wrap_text=True, vertical='top')
wb.save('Paper1_Site_Criteria_Data.xlsx'); print('ok')
