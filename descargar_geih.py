"""
Script para descargar y organizar los datos GEIH de años faltantes.
Usa DescargadorDANE del paquete geih-analisis.
"""
import os
from geih import DescargadorDANE, ConfigGEIH

RUTA_GEIH = os.path.join(os.path.dirname(__file__), "GEIH")

def descargar_anio(anio, n_meses=12):
    """Intenta descargar automáticamente un año completo de la GEIH."""
    print(f"\n{'='*60}")
    print(f"  DESCARGA GEIH {anio} ({n_meses} meses)")
    print(f"{'='*60}\n")
    
    config = ConfigGEIH(anio=anio, n_meses=n_meses)
    desc = DescargadorDANE(config=config, ruta_destino=RUTA_GEIH)
    
    # Intentar descarga automática
    print("[*] Intentando descarga automática desde microdatos.dane.gov.co...")
    resultados = desc.descargar_todos()
    
    # Mostrar resultados
    exitosos = sum(1 for v in resultados.values() if v == 'ok')
    fallidos = sum(1 for v in resultados.values() if v != 'ok')
    
    print(f"\n[*] Resultado: {exitosos} exitosos, {fallidos} fallidos")
    for mes, estado in resultados.items():
        icono = "✅" if estado == "ok" else "❌"
        print(f"    {icono} {mes}: {estado}")
    
    if fallidos > 0:
        print(f"\n[!] Algunos meses fallaron. Mostrando instrucciones manuales...")
        desc.instrucciones_descarga_manual()
    
    # Verificar estructura final
    print(f"\n[*] Verificando estructura de carpetas...")
    verif = desc.verificar()
    
    return resultados

if __name__ == "__main__":
    # Solo 2022 - ya tienes 2024 y 2025
    descargar_anio(2022, 12)
