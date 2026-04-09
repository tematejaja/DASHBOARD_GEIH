"""
Script robusto para organizar ZIPs del DANE (GEIH 2022/2023).
Maneja las 4 variantes de empaquetado del DANE:
  A) CSV sueltos dentro de carpeta/CSV/
  B) CSV.zip anidado dentro del ZIP principal
  C) Typo CVS/ en vez de CSV/ (Diciembre 2022)
  D) CSVs directamente bajo CSV/ sin prefijo de mes (Junio 2023+)
"""
import zipfile
import os
import io
import shutil
import tempfile

GEIH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GEIH")

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# Mapeo EXPLICITO de cada ZIP a su mes y anio
ZIP_MAP = {
    # ─── 2022 ────────────────────────────────────────────
    "GEIH_Enero_2022_Marco_2018.zip":          ("Enero", 2022),
    "GEIH_Febrero_2022_Marco_2018.zip":        ("Febrero", 2022),
    "GEIH_Marzo_2022_Marco_2018.zip":          ("Marzo", 2022),
    "GEIH_Abril_2022_Marco_2018_Act.zip":      ("Abril", 2022),
    "GEIH_Mayo_2022_Marco_2018.zip":           ("Mayo", 2022),
    "GEIH_Junio_2022_Marco_2018.zip":          ("Junio", 2022),
    "GEIH_Julio_2022_Marco_2018.zip":          ("Julio", 2022),
    "GEIH_Agosto_2022_Marco_2018.zip":         ("Agosto", 2022),
    "GEIH_Septiembre_Marco_2018.zip":          ("Septiembre", 2022),
    "GEIH_Octubre_Marco_2018.zip":             ("Octubre", 2022),
    "GEIH_Noviembre_2022_Marco_2018.act.zip":  ("Noviembre", 2022),
    "GEIH_Diciembre_2022_Marco_2018.zip":      ("Diciembre", 2022),
    # ─── 2023 ────────────────────────────────────────────
    "Enero 2023.zip":      ("Enero", 2023),
    "Febrero 2023.zip":    ("Febrero", 2023),
    "Marzo 2023.zip":      ("Marzo", 2023),
    "Abril 2023.zip":      ("Abril", 2023),
    "Mayo.zip":            ("Mayo", 2023),
    "Junio 2023.zip":      ("Junio", 2023),
    "Julio 2023.zip":      ("Julio", 2023),
    "Agosto 2023.zip":     ("Agosto", 2023),
    "Septiembre 2023.zip": ("Septiembre", 2023),
    "Octubre 2023.zip":    ("Octubre", 2023),
    "Noviembre 2023.zip":  ("Noviembre", 2023),
    "Diciembre 2023.zip":  ("Diciembre", 2023),
}


def extraer_csvs_de_zip_interno(zip_outer, inner_zip_name, carpeta_destino):
    """Extrae CSVs de un ZIP anidado (ZIP dentro de ZIP)."""
    with zip_outer.open(inner_zip_name) as inner_file:
        inner_bytes = io.BytesIO(inner_file.read())
        with zipfile.ZipFile(inner_bytes) as zf_inner:
            count = 0
            for info in zf_inner.infolist():
                if info.file_size > 0 and info.filename.lower().endswith('.csv'):
                    filename = os.path.basename(info.filename)
                    dest = os.path.join(carpeta_destino, filename)
                    with zf_inner.open(info) as src, open(dest, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    count += 1
            return count


def organizar_zip(zip_path, mes, anio):
    """Extrae CSVs de un ZIP del DANE (maneja todas las variantes)."""
    carpeta_destino = os.path.join(GEIH_DIR, f"{mes} {anio}", "CSV")
    
    # Si ya existe y tiene 8+ archivos, saltar
    if os.path.exists(carpeta_destino):
        csvs = [f for f in os.listdir(carpeta_destino) if f.lower().endswith('.csv')]
        if len(csvs) >= 8:
            print(f"  [=] {mes} {anio}: ya organizado ({len(csvs)} CSVs). Saltando.")
            return True
    
    os.makedirs(carpeta_destino, exist_ok=True)
    extracted = 0
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        entries = zf.infolist()
        
        # Caso 1: Hay un CSV.zip interno (ZIP anidado)
        csv_zips = [e for e in entries if e.filename.lower().endswith('csv.zip') 
                    or e.filename.lower().endswith('csv 4.zip')]
        if csv_zips:
            for csv_zip_entry in csv_zips:
                extracted += extraer_csvs_de_zip_interno(zf, csv_zip_entry.filename, carpeta_destino)
        else:
            # Caso 2: CSVs sueltos - buscar en /CSV/ o /CVS/ (typo del DANE)
            for info in entries:
                if info.file_size == 0:
                    continue
                lower = info.filename.lower()
                # Aceptar /csv/ y /cvs/ (typo DANE en Dic 2022)
                is_csv_folder = '/csv/' in lower or '/cvs/' in lower
                is_csv_file = lower.endswith('.csv')
                
                if is_csv_folder and is_csv_file:
                    filename = os.path.basename(info.filename)
                    dest = os.path.join(carpeta_destino, filename)
                    with zf.open(info) as src, open(dest, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    extracted += 1
    
    if extracted >= 8:
        print(f"  [OK] {mes} {anio}: {extracted} CSVs extraidos")
        return True
    else:
        print(f"  [!!] {mes} {anio}: solo {extracted} CSVs (esperados >= 8)")
        if os.path.exists(carpeta_destino):
            for f in sorted(os.listdir(carpeta_destino)):
                print(f"       - {f}")
        return False


def main():
    print("=" * 60)
    print("  ORGANIZACION ROBUSTA DE ZIPS GEIH 2022 + 2023")
    print("=" * 60)
    
    resultados = {}
    
    for zip_name, (mes, anio) in ZIP_MAP.items():
        zip_path = os.path.join(GEIH_DIR, zip_name)
        if not os.path.exists(zip_path):
            print(f"  [X] {zip_name} NO ENCONTRADO!")
            resultados[f"{mes} {anio}"] = False
            continue
        resultados[f"{mes} {anio}"] = organizar_zip(zip_path, mes, anio)
    
    # Verificacion final
    print(f"\n{'='*60}")
    print("  VERIFICACION FINAL")
    print(f"{'='*60}")
    
    for anio in [2022, 2023]:
        ok_count = 0
        print(f"\n  --- {anio} ---")
        for mes in MESES:
            carpeta = os.path.join(GEIH_DIR, f"{mes} {anio}", "CSV")
            if os.path.exists(carpeta):
                csvs = [f for f in os.listdir(carpeta) if f.lower().endswith('.csv')]
                icon = "OK" if len(csvs) >= 8 else "!!"
                print(f"  [{icon}] {mes} {anio}: {len(csvs)} CSVs")
                if len(csvs) >= 8:
                    ok_count += 1
            else:
                print(f"  [XX] {mes} {anio}: CARPETA NO EXISTE")
        
        status = "COMPLETO" if ok_count == 12 else f"INCOMPLETO ({ok_count}/12)"
        print(f"  >>> {anio}: {status}")


if __name__ == "__main__":
    main()
