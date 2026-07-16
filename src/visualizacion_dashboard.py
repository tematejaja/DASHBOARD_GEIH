"""Preparacion verificable de datos para las visualizaciones del dashboard."""

from __future__ import annotations

import textwrap

import numpy as np
import pandas as pd


def wrap_label(value: object, width: int = 30) -> str:
    """Envuelve una etiqueta larga sin abreviar ni cambiar su contenido."""
    text = str(value)
    return "<br>".join(
        textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    ) or text


def prepare_rama_sexo(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Normaliza ramas por sexo a millones y valida la identidad poblacional."""
    current = {"RAMA", "Hombres", "Mujeres", "Total"}
    legacy = {"Rama", "Hombre_M", "Mujer_M"}

    if current.issubset(df.columns):
        normalized = df[["RAMA", "Hombres", "Mujeres", "Total"]].rename(
            columns={"RAMA": "Rama"}
        ).copy()
        for column in ("Hombres", "Mujeres", "Total"):
            normalized[column] = pd.to_numeric(normalized[column], errors="raise")
        if normalized[["Hombres", "Mujeres", "Total"]].isna().any().any():
            raise ValueError("La distribucion por sexo contiene valores faltantes.")
        if (normalized[["Hombres", "Mujeres", "Total"]] < 0).any().any():
            raise ValueError("La distribucion por sexo contiene valores negativos.")
        if not np.allclose(
            normalized["Hombres"] + normalized["Mujeres"],
            normalized["Total"],
            rtol=1e-9,
            atol=1e-6,
        ):
            raise ValueError("Hombres y mujeres no reproducen el total de ocupados.")
        normalized[["Hombres", "Mujeres", "Total"]] /= 1_000_000
    elif legacy.issubset(df.columns):
        normalized = df[["Rama", "Hombre_M", "Mujer_M"]].rename(
            columns={"Hombre_M": "Hombres", "Mujer_M": "Mujeres"}
        ).copy()
        for column in ("Hombres", "Mujeres"):
            normalized[column] = pd.to_numeric(normalized[column], errors="raise")
        if normalized[["Hombres", "Mujeres"]].isna().any().any():
            raise ValueError("La distribucion por sexo contiene valores faltantes.")
        if (normalized[["Hombres", "Mujeres"]] < 0).any().any():
            raise ValueError("La distribucion por sexo contiene valores negativos.")
        normalized["Total"] = normalized["Hombres"] + normalized["Mujeres"]
    else:
        expected = sorted(current)
        raise ValueError(f"Esquema de rama y sexo no reconocido. Se esperaba: {expected}.")

    normalized = normalized.nlargest(top_n, "Total").sort_values("Total")
    normalized["Rama_etiqueta"] = normalized["Rama"].map(
        lambda value: wrap_label(value, width=28)
    )
    plot = normalized.melt(
        id_vars=["Rama", "Rama_etiqueta", "Total"],
        value_vars=["Hombres", "Mujeres"],
        var_name="Sexo",
        value_name="Personas_M",
    )
    return plot
