
from pathlib import Path

import pandas as pd


# ==========================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================

RAIZ = Path(__file__).resolve().parent.parent

ARCHIVO_ENTRADA = RAIZ / "data" / "limpio" / "retos_limpio.csv"
CARPETA_SALIDA = RAIZ / "data" / "limpio"


# ==========================================
# 2. CONSULTA 1: RETOS EN CURSO
# ==========================================

def consulta_1_en_curso(df):
    print("\n" + "=" * 60)
    print("CONSULTA 1: RETOS QUE ESTÁN EN CURSO")
    print("=" * 60)

    en_curso = df[df["estado"] == "EN_CURSO"]

    print(en_curso.to_string(index=False))
    print(f"\nTotal de retos en curso: {len(en_curso)}")

    en_curso.to_csv(
        CARPETA_SALIDA / "retos_consulta_1.csv",
        index=False,
        encoding="utf-8-sig",
    )

    return en_curso


# ==========================================
# 3. CONSULTA 2: LOS 10 RETOS MÁS LARGOS
# ==========================================

def consulta_2_mas_largos(df):
    print("\n" + "=" * 60)
    print("CONSULTA 2: LOS 10 RETOS MÁS LARGOS")
    print("=" * 60)

    largos = df.nlargest(
        10, "duracion_dias"
    )[["nombre", "duracion_dias", "estado"]]

    print(largos.to_string(index=False))

    largos.to_csv(
        CARPETA_SALIDA / "retos_consulta_2.csv",
        index=False,
        encoding="utf-8-sig",
    )

    return largos


# ==========================================
# 4. CONSULTA 3: CANTIDAD DE RETOS POR ESTADO
# ==========================================

def consulta_3_por_estado(df):
    print("\n" + "=" * 60)
    print("CONSULTA 3: CANTIDAD DE RETOS POR ESTADO")
    print("=" * 60)

    conteo = df["estado"].value_counts()
    resultado = conteo.rename_axis("estado").to_frame(
        name="cantidad"
    )

    print(resultado.to_string())

    resultado.to_csv(
        CARPETA_SALIDA / "retos_consulta_3.csv",
        encoding="utf-8-sig",
    )

    return resultado


# ==========================================
# 5. CONSULTA 4: DURACIÓN POR ESTADO (GROUPBY)
# ==========================================

def consulta_4_duracion_por_estado(df):
    print("\n" + "=" * 60)
    print("CONSULTA 4: DURACIÓN POR ESTADO")
    print("=" * 60)

    resumen = df.groupby("estado")["duracion_dias"].agg(
        ["count", "mean", "max"]
    )

    # Renombrar columnas para que el resultado sea claro.
    resumen = resumen.rename(
        columns={
            "count": "cantidad",
            "mean": "duracion_promedio",
            "max": "duracion_maxima",
        }
    )

    print(resumen.to_string())

    resumen.to_csv(
        CARPETA_SALIDA / "retos_consulta_4.csv",
        encoding="utf-8-sig",
    )

    return resumen


# ==========================================
# 6. CONSULTA 5: RETOS QUE EMPIEZAN POR MES (GROUPBY)
# ==========================================

def consulta_5_por_mes(df):
    print("\n" + "=" * 60)
    print("CONSULTA 5: CANTIDAD DE RETOS QUE EMPIEZAN CADA MES")
    print("=" * 60)

    # Convertir fecha_inicio a fecha si aún no lo está.
    fechas = pd.to_datetime(
        df["fecha_inicio"],
        errors="raise",
    )

    # Agrupar por año y mes.
    por_mes = df.groupby(
        fechas.dt.to_period("M")
    )["id"].count()

    resultado = por_mes.rename(
        "cantidad_retos"
    ).rename_axis("mes").to_frame()

    print(resultado.to_string())

    # Guardar el mes como texto YYYY-MM en el CSV.
    resultado.index = resultado.index.astype(str)

    resultado.to_csv(
        CARPETA_SALIDA / "retos_consulta_5.csv",
        encoding="utf-8-sig",
    )

    return resultado


# ==========================================
# 7. EJECUCIÓN PRINCIPAL
# ==========================================


def main():
    # Crear el CSV limpio automáticamente si no existe.
    if not ARCHIVO_ENTRADA.exists():
        print("No existe el archivo limpio. Iniciando limpieza...")

        from limpiar_retos import limpiar_retos

        limpiar_retos()

    # Leer el archivo limpio.
    df = pd.read_csv(
        ARCHIVO_ENTRADA,
        parse_dates=["fecha_inicio", "fecha_fin"],
    )

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

    # Ejecutar las cinco consultas en orden.
    consulta_1_en_curso(df)
    consulta_2_mas_largos(df)
    consulta_3_por_estado(df)
    consulta_4_duracion_por_estado(df)
    consulta_5_por_mes(df)

    print("\nCONSULTAS FINALIZADAS CORRECTAMENTE")
    print(f"Resultados guardados en: {CARPETA_SALIDA}")


if __name__ == "__main__":
    main()