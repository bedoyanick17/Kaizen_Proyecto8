
import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

RAIZ = Path(__file__).resolve().parent.parent

ARCHIVO_LIMPIO = RAIZ / "data" / "limpio" / "retos_limpio.csv"
ARCHIVO_SUCI0 = RAIZ / "data" / "retos_sucios.csv"
CARPETA_REPORTES = RAIZ / "reportes"


# ==========================================
# 2. CARGAR LOS DATOS
# ==========================================

def cargar_datos():
    if not ARCHIVO_LIMPIO.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo limpio: {ARCHIVO_LIMPIO}\n"
            "Ejecuta primero la etapa de limpieza."
        )

    df = pd.read_csv(ARCHIVO_LIMPIO)

    df["fecha_inicio"] = pd.to_datetime(
        df["fecha_inicio"], errors="coerce"
    )

    df["fecha_fin"] = pd.to_datetime(
        df["fecha_fin"], errors="coerce"
    )

    df["duracion_dias"] = pd.to_numeric(
        df["duracion_dias"], errors="coerce"
    )

    return df


# ==========================================
# 3. GRÁFICA 1: RETOS POR ESTADO
# ==========================================

def grafica_retos_por_estado(df):
    conteo = df["estado"].value_counts().sort_index()

    ax = conteo.plot(kind="bar")

    ax.set_title("Cantidad de retos por estado")
    ax.set_xlabel("Estado del reto")
    ax.set_ylabel("Cantidad de retos")

    plt.tight_layout()
    plt.savefig(
        CARPETA_REPORTES / "retos_grafica_1.png",
        dpi=120,
    )
    plt.close()

    return conteo


# ==========================================
# 4. GRÁFICA 2: RETOS POR MES
# ==========================================

def grafica_retos_por_mes(df):
    fechas_validas = df.dropna(subset=["fecha_inicio"])

    por_mes = (
        fechas_validas
        .groupby(
            fechas_validas["fecha_inicio"].dt.to_period("M")
        )["id"]
        .count()
    )

    # Convertir el índice a texto para mostrar año y mes.
    por_mes.index = por_mes.index.astype(str)

    ax = por_mes.plot(kind="line", marker="o")

    ax.set_title("Cantidad de retos que comienzan cada mes")
    ax.set_xlabel("Mes de inicio")
    ax.set_ylabel("Cantidad de retos")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(
        CARPETA_REPORTES / "retos_grafica_2.png",
        dpi=120,
    )
    plt.close()

    return por_mes


# ==========================================
# 5. GRÁFICA 3: DISTRIBUCIÓN DE DURACIONES
# ==========================================

def grafica_duracion(df):
    duraciones = df["duracion_dias"].dropna()

    ax = duraciones.plot(kind="hist", bins=20)

    ax.set_title("Distribución de la duración de los retos")
    ax.set_xlabel("Duración (días)")
    ax.set_ylabel("Frecuencia")

    plt.tight_layout()
    plt.savefig(
        CARPETA_REPORTES / "retos_grafica_3.png",
        dpi=120,
    )
    plt.close()

    return duraciones


# ==========================================
# 6. CONTAR FECHAS INCORRECTAS ORIGINALES
# ==========================================

def contar_fechas_incorrectas():
    """
    Cuenta las filas del CSV sucio donde la fecha de fin
    era anterior a la fecha de inicio, antes de la limpieza.
    """

    if not ARCHIVO_SUCI0.exists():
        return None

    df_sucio = pd.read_csv(ARCHIVO_SUCI0)

    inicio = pd.to_datetime(
        df_sucio["fecha_inicio"],
        format="mixed",
        dayfirst=True,
        errors="coerce",
    )

    fin = pd.to_datetime(
        df_sucio["fecha_fin"],
        format="mixed",
        dayfirst=True,
        errors="coerce",
    )

    incorrectas = (
        inicio.notna()
        & fin.notna()
        & (fin < inicio)
    )

    return int(incorrectas.sum())


# ==========================================
# 7. IMPRIMIR CONCLUSIONES
# ==========================================

def imprimir_conclusiones(df, por_mes, duraciones):
    print("\n" + "=" * 65)
    print("CONCLUSIONES DEL ANÁLISIS DE RETOS")
    print("=" * 65)

    # Mes con mayor cantidad de retos.
    if not por_mes.empty:
        mes_maximo = por_mes.idxmax()
        cantidad_maxima = int(por_mes.max())

        print(
            f"\n1. MES CON MÁS RETOS:\n"
            f"En {mes_maximo} comenzaron {cantidad_maxima} retos."
        )

        print(
            "Posible explicación: puede reflejar una mayor actividad "
            "del proyecto durante ese mes. Para confirmar la causa, "
            "se necesitaría información adicional."
        )
    else:
        print("\n1. No hay fechas de inicio válidas para analizar.")

    # Duración promedio por estado.
    print("\n2. DURACIÓN PROMEDIO POR ESTADO:")

    resumen = (
        df.groupby("estado")["duracion_dias"]
        .mean()
        .sort_index()
    )

    if resumen.empty:
        print("No hay duraciones válidas.")
    else:
        for estado, promedio in resumen.items():
            if pd.notna(promedio):
                print(f"- {estado}: {promedio:.2f} días")
            else:
                print(f"- {estado}: sin datos de duración válidos")

    if not duraciones.empty:
        print(
            f"Duración promedio general: "
            f"{duraciones.mean():.2f} días."
        )

    # Fechas de fin anteriores al inicio.
    print("\n3. FECHAS DE FIN ANTERIORES AL INICIO:")

    incorrectas = contar_fechas_incorrectas()

    if incorrectas is None:
        print(
            "No se encontró el CSV sucio para comprobar "
            "cuántas fechas incorrectas existían antes de limpiar."
        )
    else:
        print(
            f"Se encontraron {incorrectas} registros cuya fecha "
            "de fin era anterior a la fecha de inicio."
        )

    print(
        "Recomendación para el backend: validar que fecha_fin "
        "sea posterior o igual a fecha_inicio antes de guardar "
        "o actualizar un reto."
    )


# ==========================================
# 8. EJECUCIÓN PRINCIPAL
# ==========================================

def main():
    # Crear la carpeta de reportes automáticamente.
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    df = cargar_datos()

    print("Datos cargados correctamente.")
    print(f"Total de registros limpios: {len(df)}")

    print("\nGenerando gráfica 1...")
    grafica_retos_por_estado(df)

    print("Generando gráfica 2...")
    por_mes = grafica_retos_por_mes(df)

    print("Generando gráfica 3...")
    duraciones = grafica_duracion(df)

    imprimir_conclusiones(df, por_mes, duraciones)

    print("\n" + "=" * 65)
    print("REPORTE FINALIZADO")
    print(f"Gráficas guardadas en: {CARPETA_REPORTES}")
    print("=" * 65)


if __name__ == "__main__":
    main()