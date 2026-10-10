
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_SUCIO = RAIZ / "data" / "retos_sucios.csv"
CARPETA_LIMPIA = RAIZ / "data" / "limpio"
ARCHIVO_LIMPIO = CARPETA_LIMPIA / "retos_limpio.csv"


def limpiar_retos():
    if not ARCHIVO_SUCIO.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo sucio: {ARCHIVO_SUCIO}"
        )

    CARPETA_LIMPIA.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ARCHIVO_SUCIO)

    # Limpiar espacios y normalizar nombres.
    df["nombre"] = (
        df["nombre"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    # Normalizar descripciones sin convertir los nulos en texto.
    df["descripcion"] = (
        df["descripcion"]
        .astype("string")
        .str.strip()
    )

    # Normalizar los estados.
    estados = {
        "pendiente": "PENDIENTE",
        "en_curso": "EN_CURSO",
        "en curso": "EN_CURSO",
        "completado": "COMPLETADO",
        "cerrado": "CERRADO",
    }

    df["estado"] = (
        df["estado"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map(estados)
    )

    # Normalizar identificadores UUID en minúsculas.
    for columna in [
        "id",
        "id_empresa",
        "id_categoria",
        "id_prioridad",
    ]:
        df[columna] = (
            df[columna]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # Convertir las fechas, admitiendo formatos diferentes.
    for columna in ["fecha_inicio", "fecha_fin"]:
        df[columna] = pd.to_datetime(
            df[columna],
            format="mixed",
            dayfirst=True,
            errors="coerce",
        )

    # Eliminar filas duplicadas exactas.
    df = df.drop_duplicates()

    # Eliminar registros sin identificador o fecha de inicio.
    df = df.dropna(subset=["id", "fecha_inicio"])

    # Eliminar filas con fechas de fin anteriores al inicio.
    fechas_incorrectas = (
        df["fecha_fin"].notna()
        & (df["fecha_fin"] < df["fecha_inicio"])
    )
    df.loc[fechas_incorrectas, "fecha_fin"] = pd.NaT

    # Calcular duración en días.
    df["duracion_dias"] = (
        df["fecha_fin"] - df["fecha_inicio"]
    ).dt.days

    # Guardar fechas en formato uniforme.
    df["fecha_inicio"] = df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    df["fecha_fin"] = df["fecha_fin"].dt.strftime("%Y-%m-%d")

    df.to_csv(
        ARCHIVO_LIMPIO,
        index=False,
        encoding="utf-8-sig",
    )

    print("Limpieza finalizada correctamente.")
    print(f"Registros limpios: {len(df)}")
    print(f"Archivo generado: {ARCHIVO_LIMPIO}")

    return df


if __name__ == "__main__":
    limpiar_retos()
