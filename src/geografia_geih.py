"""Registro canonico de dominios urbanos autorrepresentados de la GEIH."""

from __future__ import annotations

import pandas as pd


DOMINIOS_GEIH = [
    ("05", "Medellín A.M.", "Área metropolitana", "Medellín; Bello; Envigado; Itagüí; Caldas; Copacabana; Girardota; La Estrella; Sabaneta"),
    ("08", "Barranquilla A.M.", "Área metropolitana", "Barranquilla; Malambo; Soledad; Puerto Colombia"),
    ("11", "Bogotá D.C.", "Ciudad", "Bogotá D.C."),
    ("13", "Cartagena", "Ciudad", "Cartagena"),
    ("15", "Tunja", "Ciudad", "Tunja"),
    ("17", "Manizales A.M.", "Área metropolitana", "Manizales; Villamaría"),
    ("18", "Florencia", "Ciudad", "Florencia"),
    ("19", "Popayán", "Ciudad", "Popayán"),
    ("20", "Valledupar", "Ciudad", "Valledupar"),
    ("23", "Montería", "Ciudad", "Montería"),
    ("27", "Quibdó", "Ciudad", "Quibdó"),
    ("41", "Neiva", "Ciudad", "Neiva"),
    ("44", "Riohacha", "Ciudad", "Riohacha"),
    ("47", "Santa Marta", "Ciudad", "Santa Marta"),
    ("50", "Villavicencio", "Ciudad", "Villavicencio"),
    ("52", "Pasto", "Ciudad", "Pasto"),
    ("54", "Cúcuta A.M.", "Área metropolitana", "Cúcuta; Villa del Rosario; Los Patios; El Zulia"),
    ("63", "Armenia", "Ciudad", "Armenia"),
    ("66", "Pereira A.M.", "Área metropolitana", "Pereira; Dosquebradas; La Virginia"),
    ("68", "Bucaramanga A.M.", "Área metropolitana", "Bucaramanga; Floridablanca; Girón; Piedecuesta"),
    ("70", "Sincelejo", "Ciudad", "Sincelejo"),
    ("73", "Ibagué", "Ciudad", "Ibagué"),
    ("76", "Cali A.M.", "Área metropolitana", "Cali; Yumbo"),
    ("81", "Arauca", "Cabecera capital", "Arauca"),
    ("85", "Yopal", "Cabecera capital", "Yopal"),
    ("86", "Mocoa", "Cabecera capital", "Mocoa"),
    ("88", "San Andrés", "Cabecera capital", "San Andrés"),
    ("91", "Leticia", "Cabecera capital", "Leticia"),
    ("94", "Inírida", "Cabecera capital", "Inírida"),
    ("95", "San José del Guaviare", "Cabecera capital", "San José del Guaviare"),
    ("97", "Mitú", "Cabecera capital", "Mitú"),
    ("99", "Puerto Carreño", "Cabecera capital", "Puerto Carreño"),
]

AREA_A_DOMINIO = {codigo: nombre for codigo, nombre, _, _ in DOMINIOS_GEIH}


def normalizar_area(area: pd.Series) -> pd.Series:
    """Normaliza AREA sin convertir faltantes o blancos en codigos espurios."""
    texto = area.astype("string").str.strip()
    numerico = pd.to_numeric(texto, errors="coerce").astype("Int64")
    return numerico.astype("string").str.zfill(2)


def asignar_dominio(area: pd.Series) -> pd.Series:
    return normalizar_area(area).map(AREA_A_DOMINIO)


def dataframe_dominios() -> pd.DataFrame:
    return pd.DataFrame(
        DOMINIOS_GEIH,
        columns=["AREA", "Dominio", "Tipo_dominio", "Municipios_integrantes"],
    ).assign(Vigencia="GEIH marco 2018")
