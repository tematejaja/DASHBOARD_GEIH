import os
import argparse
from geih import ConfigGEIH, ConsolidadorGEIH, DescargadorDANE

# --- Configuración Inicial ---
# Año de la GEIH a analizar y cantidad de meses esperada.
# Por defecto lo configuramos a 2025 (asumiendo que estamos en 2026 y queremos el año completo cerrado)
DEFAULT_ANIO = 2025
DEFAULT_MESES = 12

def consolidar_datos(anio=DEFAULT_ANIO, meses=DEFAULT_MESES, ruta_base="data/GEIH"):
    """
    Función que revisa los CSV y genera el parquet de la GEIH uniendo los módulos mensuales.
    """
    print(f"[*] Iniciando Pipeline de Ingesta para GEIH {anio} ({meses} meses)")
    
    # 1. Configuración de parámetros de la encuesta
    config = ConfigGEIH(anio=anio, n_meses=meses)
    config.resumen()
    
    # 2. Verificar existencia de carpeta y archivos.
    # El paquete exige una estructura como: data/GEIH/Enero 2025/CSV/...
    if not os.path.exists(ruta_base):
        os.makedirs(ruta_base)
        print(f"\n[!] ADVERTENCIA: La carpeta {ruta_base} estaba vacía y fue creada.")
        print(f"Por favor, descarga los archivos .zip desde microdatos.dane.gov.co,")
        print(f"y almacénalos aquí. Luego, vuelve a ejecutar el script.")
        return False
        
    print(f"\n[*] Analizando estructura de directorios en {ruta_base}...")
    cons = ConsolidadorGEIH(ruta_base=ruta_base, config=config, incluir_area=True)
    
    try:
        # Esto arrojará una excepción si los archivos no están completos
        cons.verificar_estructura()
    except Exception as e:
        print(f"\n[ERROR] Estructura CSV incompleta: {e}")
        print("💡 Sugerencia: Si tienes los archivos .zip sin procesar en otra ruta,")
        print("el paquete tiene una herramienta 'DescargadorDANE.organizar_zips()'.")
        return False

    print("\n[+] Estructura verificada correctamente. Iniciando Consolidación a Parquet...")
    print("   (Este proceso tardará ~5 minutos la primera vez y consumirá memoria).")
    
    # 3. Consolidar (con checkpointing auto en caso de fallo por falta de RAM local)
    df_consolidado = cons.consolidar(checkpoint=True)
    
    # 4. Guardar resultado unificado
    cons.exportar(df_consolidado)
    
    parquet_path = os.path.join(ruta_base, f"GEIH_{anio}_Consolidado.parquet")
    print(f"\n[✅] ¡Exito! Parquet guardado en: {parquet_path}")
    print(f"   Filas procesadas: {len(df_consolidado):,}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingesta y Consolidación GEIH")
    parser.add_argument("--anio", type=int, default=DEFAULT_ANIO, help="Año de la GEIH a consolidar")
    parser.add_argument("--meses", type=int, default=DEFAULT_MESES, help="Número de meses de la GEIH a consolidar")
    args = parser.parse_args()
    
    os.makedirs('GEIH', exist_ok=True)
    consolidar_datos(args.anio, args.meses, "GEIH")
