"""Restrict the candidate set to the 16 metros covered by Cushman & Wakefield (decision of Nov 11, 2026)."""
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
F = 'Paper1_Site_Criteria_Data.xlsx'
all20 = pd.read_excel(F, sheet_name='Criteria by metro', dtype={'CBSA': str})
defs = pd.read_excel(F, sheet_name='Criteria definitions')
keep = all20[all20['In C&W (16-market set)'] == 'Yes'].drop(columns=['In C&W (16-market set)', 'C1 source'])
excl = all20[all20['In C&W (16-market set)'] == 'No'][['CBSA', 'Metro', 'Population 2024']].copy()
excl['Reason excluded'] = 'Not a Cushman & Wakefield MarketBeat market; no Q3 2026 warehouse rent from a comparable source'
defs.loc[defs.Code == 'C1', 'Notes'] = 'Single source and quarter for all 16 candidate metros.'
rule = pd.DataFrame({'Candidate-site rule': [
    'Candidate sites are the Metropolitan Statistical Areas whose principal state is in the Census Midwest region '
    '(IL, IN, IA, KS, MI, MN, MO, NE, ND, OH, SD, WI) with a 2024 population of at least 500,000, plus the border metros '
    'Louisville and Pittsburgh, that are covered by the Cushman & Wakefield U.S. Industrial MarketBeat. This gives 16 metros.',
    'Restricting to C&W markets ensures that every warehouse rent comes from one source, one method and one quarter (Q3 2026).',
    'Excluded by the coverage requirement: Dayton, Akron, Wichita and Toledo (see sheet "Excluded metros"). '
    'Springfield, MO (497,000) falls just below the population cutoff.']})
with pd.ExcelWriter(F, engine='openpyxl') as w:
    keep.to_excel(w, sheet_name='Criteria by metro', index=False)
    defs.to_excel(w, sheet_name='Criteria definitions', index=False)
    rule.to_excel(w, sheet_name='Candidate rule', index=False)
    excl.to_excel(w, sheet_name='Excluded metros', index=False)
    all20.to_excel(w, sheet_name='All 20 (reference)', index=False)
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
keep.to_csv('raw/site_criteria_16.csv', index=False)
print(keep[['Metro', 'C1 W/D asking rent Q3 2026 ($/sf/yr)', 'C2 Warehouse laborer mean wage May 2025 ($/hr)']].to_string(index=False))
