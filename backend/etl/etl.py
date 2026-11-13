from pathlib import Path
from decimal import Decimal
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.engine import URL
from sqlalchemy.dialects.mysql import insert
import os
from calculos import calcular_monto_total, calcular_igv
from validaciones import (
    limpiar_texto,
    normalizar_categoria,
    limpiar_precio,
    limpiar_entero
)

BASE_DIR = Path(__file__).resolve().parent.parent

CENTIMOS = Decimal("0.01")

ARCHIVO_ENTRADA = BASE_DIR / "etl" / "ventas_departamentos_sucio_v2.csv"

COLUMNAS = [
    "id_transaccion",
    "categoria",
    "producto",
    "cantidad",
    "precio_unitario",
    "fecha_venta",
    "stock_actual",
]

# extraer
def extraer_datos():

    df = pd.read_csv(
        ARCHIVO_ENTRADA,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    df.columns = df.columns.str.strip()

    faltantes = set(COLUMNAS) - set(df.columns)

    if faltantes:
        raise ValueError(
            f"Faltan columnas obligatorias: {sorted(faltantes)}"
        )

    df = df[COLUMNAS].copy()

    print(f"Registros originales: {len(df)}")

    return df


# transformar
def transformar_datos(df):

    total_original = len(df)

    for columna in COLUMNAS:
        df[columna] = df[columna].map(limpiar_texto)

    df["id_transaccion"] = (
        df["id_transaccion"].str.upper()
    )

    df["categoria"] = (
        df["categoria"].map(normalizar_categoria)
    )

    df["producto"] = (
        df["producto"].str.title()
    )

    df = df.drop_duplicates()
    df = df.drop_duplicates(
        subset=["id_transaccion"],
        keep="first"
    )

    df["cantidad"] = df["cantidad"].map(limpiar_entero)
    df["stock_actual"] = df["stock_actual"].map(limpiar_entero)
    df["precio_unitario"] = (
        df["precio_unitario"].map(limpiar_precio)
    )

    df["fecha_venta"] = pd.to_datetime(
        df["fecha_venta"],
        format="%Y-%m-%d",
        errors="coerce",
        exact=True
    )

    df = df.dropna(subset=[
        "categoria",
        "cantidad",
        "precio_unitario",
        "fecha_venta",
        "stock_actual"
    ])

    df = df[
        (df["id_transaccion"].str.len() > 0) &
        (df["id_transaccion"].str.len() <= 15) &
        (df["producto"].str.len() > 0) &
        (df["producto"].str.len() <= 100) &
        (df["cantidad"] > 0) &
        (df["stock_actual"] >= 0)
    ].copy()

    df["monto_total"] = df.apply(
        lambda fila: calcular_monto_total(
            fila["cantidad"],
            fila["precio_unitario"]
        ),
        axis=1
    )

    df["igv"] = df["monto_total"].map(calcular_igv)

    max_decimal = Decimal("99999999.99")

    df = df[
        (df["precio_unitario"] <= max_decimal) &
        (df["monto_total"] <= max_decimal) &
        (df["igv"] <= max_decimal)
    ].copy()

    df["fecha_venta"] = df["fecha_venta"].dt.date
    df["cantidad"] = df["cantidad"].astype(int)
    df["stock_actual"] = df["stock_actual"].astype(int)

    df = df.reset_index(drop=True)

    print(f"Registros validos: {len(df)}")
    print(f"Registros omitidos: {total_original - len(df)}")

    return df


def cargar_mysql(df):

    print("Enviando datos ...")

    load_dotenv(BASE_DIR / ".env")

    url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "tienda_ventas"),
    )

    engine = create_engine(url, pool_pre_ping=True)

    metadata = MetaData()
    ventas = Table(
        "ventas",
        metadata,
        autoload_with=engine
    )

    registros = df.to_dict(orient="records")

    with engine.begin() as conexion:
        for inicio in range(0, len(registros), 500):
            lote = registros[inicio:inicio + 500]

            consulta = insert(ventas).values(lote)

            cambios = {
                columna.name: consulta.inserted[columna.name]
                for columna in ventas.columns
                if columna.name != "id_transaccion"
            }

            ## evitar duplicados, los actualiza
            consulta = consulta.on_duplicate_key_update(
                **cambios
            )

            conexion.execute(consulta)

        total_bd = conexion.execute(
            select(ventas.c.id_transaccion)
        ).fetchall()

    engine.dispose()

    print(f"Registros cargados: {len(total_bd)}")


def main():

    df = extraer_datos()

    df_limpio = transformar_datos(df)

    if df_limpio.empty:
        print("Registros vacios")
        return

    cargar_mysql(df_limpio)


if __name__ == "__main__":
    main()
