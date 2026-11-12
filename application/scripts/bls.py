import json, urllib.request, csv
metros=[("16980","Chicago","17"),("19820","Detroit","26"),("33460","Minneapolis-St. Paul","27"),("41180","St. Louis","29"),
("17140","Cincinnati","39"),("28140","Kansas City","29"),("18140","Columbus","39"),("26900","Indianapolis","18"),("17410","Cleveland","39"),
("33340","Milwaukee","55"),("31140","Louisville","21"),("24340","Grand Rapids","26"),("36540","Omaha","31"),("19430","Dayton","39"),
("19780","Des Moines","19"),("31540","Madison","55"),("10420","Akron","39"),("48620","Wichita","20"),("45780","Toledo","39"),("38300","Pittsburgh","42")]
series={}
for c,n,s in metros:
    series[f"OEUM00{c}000000537062"+"01"]=(n,'oews_emp'); series[f"OEUM00{c}000000537062"+"03"]=(n,'oews_wage')
    series[f"OEUM00{c}000000537062"+"16"]=(n,'oews_per1000')
    series[f"LAUMT{s}{c}00000003"]=(n,'unemp'); series[f"LAUMT{s}{c}00000006"]=(n,'laborforce')
ids=list(series); res={}
for i in range(0,len(ids),25):
    req=urllib.request.Request("https://api.bls.gov/publicAPI/v1/timeseries/data/",data=json.dumps({"seriesid":ids[i:i+25],"startyear":"2024","endyear":"2026"}).encode(),headers={"Content-Type":"application/json"})
    r=json.load(urllib.request.urlopen(req,timeout=60))
    if r['status']!='REQUEST_SUCCEEDED': print(r['message'])
    for s in r['Results']['series']: res[s['seriesID']]=s['data']
json.dump({'series':series,'res':res},open('raw/bls_raw.json','w'))
print(len(res))
