from datetime import date
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine


app = FastAPI(
    title="API",
    description="backend",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# to json
def convertir_registro(fila):

    resultado = dict(fila)

    for clave, valor in resultado.items():
        if isinstance(valor, Decimal):
            resultado[clave] = float(valor)

        elif isinstance(valor, date):
            resultado[clave] = valor.isoformat()

    return resultado


# inicio
@app.get("/")
def inicio():
    return {
        "mensaje": "API de Ventas por Departamentos",
        "version": "1.0",
    }

# paginacio, evitar +400 respuestas
@app.get("/api/ventas")
def obtener_ventas(
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=100),
    buscar: str = Query(default="", max_length=100),
):
    offset = (pagina - 1) * limite

    buscar = (
        buscar.strip()
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )

    parametros = {
        "buscar": f"%{buscar}%",
        "limite": limite,
        "offset": offset
    }

    condicion = """
        WHERE (
            id_transaccion LIKE :buscar
            OR categoria LIKE :buscar
            OR producto LIKE :buscar
        )
    """

    consulta = text(f"""
        SELECT
            id_transaccion,
            categoria,
            producto,
            cantidad,
            precio_unitario,
            fecha_venta,
            stock_actual,
            monto_total,
            igv
        FROM ventas
        {condicion}
        ORDER BY fecha_venta DESC, id_transaccion DESC
        LIMIT :limite OFFSET :offset
    """)

    consulta_total = text(f"""
        SELECT COUNT(*) AS total
        FROM ventas
        {condicion}
    """)

    with engine.connect() as conexion:
        filas = conexion.execute(
            consulta, parametros
        ).mappings().all()

        total = conexion.execute(
            consulta_total, parametros
        ).scalar_one()

    datos = [convertir_registro(fila) for fila in filas]

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "datos": datos
    }

@app.get("/api/ventas/{id_transaccion}")
def obtener_venta(id_transaccion: str):

    consulta = text("""
        SELECT *
        FROM ventas
        WHERE id_transaccion = :id
    """)

    with engine.connect() as conexion:
        fila = conexion.execute(
            consulta,
            {"id": id_transaccion}
        ).mappings().first()

    if fila is None:
        raise HTTPException(
            status_code=404,
            detail="Transacción no encontrada"
        )

    return convertir_registro(fila)


@app.get("/api/dashboard/ingresos")
def ingresos_por_categoria():

    consulta = text("""
        SELECT
            categoria,
            ROUND(SUM(monto_total), 2) AS monto_total,
            ROUND(SUM(igv), 2) AS igv
        FROM ventas
        GROUP BY categoria
        ORDER BY monto_total DESC
    """)

    with engine.connect() as conexion:
        filas = conexion.execute(
            consulta
        ).mappings().all()

    return {
        "datos": [
            convertir_registro(fila)
            for fila in filas
        ]
    }

@app.get("/api/dashboard/unidades")
def unidades_por_categoria():

    consulta = text("""
        SELECT
            categoria,
            SUM(cantidad) AS unidades_vendidas
        FROM ventas
        GROUP BY categoria
        ORDER BY unidades_vendidas DESC
    """)

    with engine.connect() as conexion:
        filas = conexion.execute(
            consulta
        ).mappings().all()

    total_unidades = sum(
        int(fila["unidades_vendidas"])
        for fila in filas
    )

    datos = []

    for fila in filas:
        unidades = int(fila["unidades_vendidas"])

        porcentaje = (
            round(unidades / total_unidades * 100, 2)
            if total_unidades > 0
            else 0
        )

        datos.append({
            "categoria": fila["categoria"],
            "unidades_vendidas": unidades,
            "porcentaje": porcentaje
        })

    return {
        "total_unidades": total_unidades,
        "datos": datos
    }
