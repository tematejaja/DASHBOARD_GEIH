"""Fix Junio 2023 and Septiembre 2023."""
import zipfile, os, shutil, io

GEIH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GEIH")

# --- Junio 2023: CSVs directamente bajo CSV/ ---
zip_path = os.path.join(GEIH_DIR, 'Junio 2023.zip')
dest = os.path.join(GEIH_DIR, 'Junio 2023', 'CSV')
os.makedirs(dest, exist_ok=True)
count = 0
with zipfile.ZipFile(zip_path) as zf:
    for info in zf.infolist():
        if info.file_size > 0 and info.filename.startswith('CSV/') and info.filename.lower().endswith('.csv'):
            fname = os.path.basename(info.filename)
            with zf.open(info) as src, open(os.path.join(dest, fname), 'wb') as dst:
                shutil.copyfileobj(src, dst)
            count += 1
print(f'Junio 2023: {count} CSVs extraidos')

# --- Septiembre 2023: ZIP anidado CSV 13.zip ---
zip_path = os.path.join(GEIH_DIR, 'Septiembre 2023.zip')
dest = os.path.join(GEIH_DIR, 'Septiembre 2023', 'CSV')
os.makedirs(dest, exist_ok=True)
count = 0
with zipfile.ZipFile(zip_path) as zf:
    inner_matches = [e.filename for e in zf.infolist() if 'csv' in e.filename.lower() and e.filename.lower().endswith('.zip')]
    inner_name = inner_matches[0]
    print(f'  ZIP interno encontrado: {inner_name}')
    with zf.open(inner_name) as inner_file:
        inner_bytes = io.BytesIO(inner_file.read())
        with zipfile.ZipFile(inner_bytes) as zf2:
            for info in zf2.infolist():
                if info.file_size > 0 and info.filename.lower().endswith('.csv'):
                    fname = os.path.basename(info.filename)
                    with zf2.open(info) as src, open(os.path.join(dest, fname), 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    count += 1
print(f'Septiembre 2023: {count} CSVs extraidos')

# Verificacion
for mes in ['Junio 2023', 'Septiembre 2023']:
    p = os.path.join(GEIH_DIR, mes, 'CSV')
    csvs = [f for f in os.listdir(p) if f.lower().endswith('.csv')]
    status = "OK" if len(csvs) >= 8 else "FALLO"
    print(f'{mes}: {len(csvs)} CSVs -> {status}')
