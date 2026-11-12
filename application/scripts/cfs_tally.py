import pandas as pd, zipfile
z=zipfile.ZipFile('raw/cfs_2022_pums.zip')
cols=['DEST_STATE','DEST_CFS_AREA','SCTG','MODE','SHIPMT_WGHT','SHIPMT_VALUE','EXPORT_YN','WGT_FACTOR']
agg=[]; dest=[]
for ch in pd.read_csv(z.open('cfs_2022_pums.csv'),usecols=cols,dtype={'DEST_STATE':str,'DEST_CFS_AREA':str,'SCTG':str,'MODE':str},chunksize=2_000_000):
    ch['tons']=ch.SHIPMT_WGHT*ch.WGT_FACTOR/2000; ch['val']=ch.SHIPMT_VALUE*ch.WGT_FACTOR
    ch['truck']=ch.MODE.isin(['111','112','113']); ch['dom']=ch.EXPORT_YN=='N'
    agg.append(ch.groupby(['SCTG','truck','dom']).agg(n=('tons','size'),tons=('tons','sum'),val=('val','sum')))
    f=ch[ch.truck&ch.dom]
    dest.append(f.groupby(['SCTG','DEST_STATE','DEST_CFS_AREA']).agg(n=('tons','size'),tons=('tons','sum')))
a=pd.concat(agg).groupby(level=[0,1,2]).sum(); a.to_csv('raw/cfs2022_tons_by_sctg_mode.csv')
d=pd.concat(dest).groupby(level=[0,1,2]).sum(); d.to_csv('raw/cfs2022_truck_domestic_by_sctg_dest.csv')
t=a.xs((True,True),level=[1,2]).sort_values('tons',ascending=False)
t['tons_M']=t.tons/1e6; t['share%']=100*t.tons/t.tons.sum(); t['val_$B']=t.val/1e9
print(t[['n','tons_M','share%','val_$B']].round(1).to_string())
