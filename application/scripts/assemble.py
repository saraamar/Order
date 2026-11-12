import json, csv, pandas as pd
bls=json.load(open('raw/bls_raw.json')); cw=json.load(open('raw/cw_q3_2026.json'))
ia=pd.read_csv('raw/interstate_access.csv',dtype={'cbsa':str})
pop={r['CBSA']:int(r['POPESTIMATE2024']) for r in csv.DictReader(open('raw/cbsa.csv',encoding='latin-1')) if r['LSAD']=='Metropolitan Statistical Area'}
cwname={'Minneapolis-St. Paul':'Minneapolis'}
months=[f'2025M{m:02d}' for m in (10,11,12)]+[f'2026M{m:02d}' for m in range(1,10)]
rows={}
for sid,(n,k) in bls['series'].items():
    data=bls['res'].get(sid,[]); r=rows.setdefault(n,{})
    if k.startswith('oews'): r[k]=float(data[0]['value']) if data and data[0]['value'] not in ('-','*') else None
    else:
        v=[float(x['value']) for x in data if x['year']+x['period'] in months and x['value'] not in ('-',)]
        r[k]=round(sum(v)/len(v),2) if v else None; r[k+'_n']=len(v)
out=[]
for _,m in ia.iterrows():
    n=m.metro; r=rows[n]; c=cw.get(cwname.get(n,n),{})
    rent=c.get('rent'); vac=c.get('vac'); inv=c.get('inv')
    f=lambda s: float(s.replace('$','').replace('%','').replace(',','')) if s and s!='n/a' else None
    out.append({'CBSA':m.cbsa,'Metro':n,'Population 2024':pop[m.cbsa],
      'C1 W/D asking rent Q3 2026 ($/sf/yr)':f(rent[5]) if rent else None,
      'C1 source':'Cushman & Wakefield U.S. Industrial MarketBeat Q3 2026' if rent else 'MISSING: not in C&W; second broker needed',
      'Overall asking rent Q3 2026 ($/sf/yr)':f(rent[4]) if rent else None,
      'C2 Warehouse laborer mean wage May 2025 ($/hr)':r['oews_wage'],
      'C3 Warehouse laborer employment May 2025':r['oews_emp'],
      'Warehouse laborers per 1,000 jobs':r['oews_per1000'],
      'C4 Unemployment rate, 12-mo avg Oct25-Sep26 (%)':r['unemp'],
      'Labor force, 12-mo avg':round(r['laborforce']) if r['laborforce'] else None,
      'Months averaged':r['unemp_n'],
      'C5 Interstate miles inside metro':m.interstate_miles,
      'C6 Mainline (2-digit) interstates':m.mainline_interstates,
      'Mainline interstate list':m.mainline_list,
      'Industrial vacancy Q3 2026 (%)':f(vac[4]) if vac else None,
      'Industrial inventory Q3 2026 (sf)':f(inv[0]) if inv else None,
      'Under construction Q3 2026 (sf)':f(inv[2]) if inv else None})
df=pd.DataFrame(out).sort_values('Population 2024',ascending=False)
df.insert(2,'In C&W (16-market set)',df['C1 W/D asking rent Q3 2026 ($/sf/yr)'].notna().map({True:'Yes',False:'No'}))
df.to_csv('raw/site_criteria.csv',index=False)
print(df.to_string(max_colwidth=18))
