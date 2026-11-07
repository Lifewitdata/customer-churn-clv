from pathlib import Path
import hashlib, io, json, urllib.request, zipfile
import pandas as pd
URL = 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip'
def load(root):
    folder = Path(root)/'data/raw'; folder.mkdir(parents=True, exist_ok=True)
    path = folder/'online_retail_II.xlsx'
    if not path.exists():
        payload = urllib.request.urlopen(URL, timeout=120).read()
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            with archive.open('online_retail_II.xlsx') as source:
                path.write_bytes(source.read())
    frame = pd.concat(pd.read_excel(path, sheet_name=None).values(), ignore_index=True)
    frame.columns = ['invoice','stock_code','description','quantity','invoice_date','unit_price','customer_id','country']
    provenance = dict(url=URL, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), rows=len(frame),
                      citation='Chen, D. (2012). Online Retail II. UCI. DOI:10.24432/C5CG6D', license='CC BY 4.0')
    (Path(root)/'reports/source_manifest.json').write_text(json.dumps(provenance,indent=2))
    return frame
