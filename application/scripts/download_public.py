"""Step 0: download the public input files into raw/ (run from the application/ folder).
The two large or third-party files (CFS PUMS, 680 MB; Cushman & Wakefield PDF) are not stored in the repository."""
import os, subprocess
os.makedirs('raw', exist_ok=True)
FILES = {
    'raw/cbsa.csv': 'https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/metro/totals/cbsa-est2024-alldata.csv',
    'raw/cb_2023_us_cbsa_500k.zip': 'https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_cbsa_500k.zip',
    'raw/list2022.xlsx': 'https://www2.census.gov/programs-surveys/cfs/technical-documentation/geographies/list2022.xlsx',
    'raw/CenPop2020_Mean_CO.txt': 'https://www2.census.gov/geo/docs/reference/cenpop2020/county/CenPop2020_Mean_CO.txt',
    'raw/cfs_2022_pums_data_dictionary.xlsx': 'https://www2.census.gov/programs-surveys/cfs/datasets/2022/cfs_2022_pums_data_dictionary.xlsx',
    'raw/cfs_2022_pums.zip': 'https://www2.census.gov/programs-surveys/cfs/datasets/2022/cfs_2022_pums.zip',
    'raw/q32026usindustrialmarketbeat.pdf': 'https://assets.cushmanwakefield.com/-/media/cw/marketbeat-pdfs/2026/q3/us-reports/national/q32026usindustrialmarketbeat.pdf',
}
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
for path, url in FILES.items():
    if os.path.exists(path):
        print('exists', path); continue
    subprocess.run(['curl', '-sSL', '-A', UA, '-o', path, url], check=True)
    print('downloaded', path)
