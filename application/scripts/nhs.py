import geopandas as gpd, pandas as pd, json, urllib.request, urllib.parse
codes={"16980":"Chicago","19820":"Detroit","33460":"Minneapolis-St. Paul","41180":"St. Louis","17140":"Cincinnati","28140":"Kansas City","18140":"Columbus","26900":"Indianapolis","17410":"Cleveland","33340":"Milwaukee","31140":"Louisville","24340":"Grand Rapids","36540":"Omaha","19430":"Dayton","19780":"Des Moines","31540":"Madison","10420":"Akron","48620":"Wichita","45780":"Toledo","38300":"Pittsburgh"}
cb=gpd.read_file('raw/cb_2023_us_cbsa_500k.zip'); cb=cb[cb.CBSAFP.isin(codes)].to_crs(4326)
URL="https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Highway_System/FeatureServer/0/query"
rows=[]
for _,m in cb.iterrows():
    x0,y0,x1,y1=m.geometry.bounds; feats=[]; off=0
    while True:
        q=dict(where="SIGNT1='I'",geometry=f"{x0},{y0},{x1},{y1}",geometryType="esriGeometryEnvelope",inSR=4326,
               spatialRel="esriSpatialRelIntersects",outFields="SIGNN1,AADT_COM,MILES",outSR=4326,f="geojson",resultOffset=off,resultRecordCount=2000)
        g=json.load(urllib.request.urlopen(URL+"?"+urllib.parse.urlencode(q),timeout=120))
        feats+=g['features']
        if not g.get('properties',{}).get('exceededTransferLimit') and len(g['features'])<2000: break
        off+=2000
    gdf=gpd.GeoDataFrame.from_features(feats,crs=4326)
    clip=gpd.clip(gdf,m.geometry).to_crs(5070); clip['mi']=clip.length/1609.344
    byroute=clip.groupby('SIGNN1').mi.sum()
    main=[r for r,v in byroute.items() if r and len(str(r).strip())<=2 and v>=1]
    # truck AADT weighted by length, use max segment truck AADT too
    tr=clip[clip.AADT_COM>0]
    rows.append(dict(cbsa=m.CBSAFP,metro=codes[m.CBSAFP],interstate_miles=round(clip.mi.sum(),1),
        mainline_interstates=len(main),mainline_list=" ".join(sorted(main,key=lambda s:int(''.join(ch for ch in s if ch.isdigit()) or 0))),
        all_interstate_routes=int((byroute>=1).sum()),
        truck_vmt_per_day=round((tr.AADT_COM*tr.mi).sum())))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('raw/interstate_access.csv',index=False)
