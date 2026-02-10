from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

DB_NAME = "taller.db"


# ============================
# CREAR BASE DE DATOS
# ============================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla autos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS autos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        carro TEXT,
        placas TEXT,
        fecha TEXT
    )
    """)

    # Tabla inventario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        cantidad INTEGER,
        precio REAL
    )
    """)

    # Tabla contabilidad
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contabilidad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        descripcion TEXT,
        monto REAL,
        fecha TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================
# HOME
# ============================
@app.route("/")
def home():
    return render_template("home.html")


# ============================
# REGISTRAR AUTO
# ============================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        cliente = request.form["cliente"]
        carro = request.form["carro"]
        placas = request.form["placas"]
        fecha = str(date.today())

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO autos (cliente, carro, placas, fecha) VALUES (?, ?, ?, ?)",
                       (cliente, carro, placas, fecha))
        conn.commit()
        conn.close()

        return redirect("/autos")

    return render_template("registro.html")


# ============================
# LISTA DE AUTOS
# ============================
@app.route("/autos")
def autos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM autos ORDER BY id DESC")
    autos = cursor.fetchall()
    conn.close()

    return render_template("autos.html", autos=autos)


# ============================
# INVENTARIO
# ============================
@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        cursor.execute("INSERT INTO inventario (nombre, cantidad, precio) VALUES (?, ?, ?)",
                       (nombre, cantidad, precio))
        conn.commit()

    cursor.execute("SELECT * FROM inventario ORDER BY id DESC")
    items = cursor.fetchall()

    conn.close()

    return render_template("inventario.html", items=items)


# ============================
# CONTABILIDAD
# ============================
@app.route("/contabilidad", methods=["GET", "POST"])
def contabilidad():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        monto = float(request.form["monto"])
        fecha = str(date.today())

        cursor.execute("""
        INSERT INTO contabilidad (tipo, descripcion, monto, fecha)
        VALUES (?, ?, ?, ?)
        """, (tipo, descripcion, monto, fecha))

        conn.commit()

    # Totales
    cursor.execute("SELECT SUM(monto) FROM contabilidad WHERE tipo='Ingreso'")
    total_ingresos = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(monto) FROM contabilidad WHERE tipo='Gasto'")
    total_gastos = cursor.fetchone()[0] or 0

    ganancia = total_ingresos - total_gastos

    # FORMATO PRO (2 decimales)
    total_ingresos = round(total_ingresos, 2)
    total_gastos = round(total_gastos, 2)
    ganancia = round(ganancia, 2)

    cursor.execute("SELECT * FROM contabilidad ORDER BY id DESC")
    movimientos = cursor.fetchall()

    conn.close()

    return render_template("contabilidad.html",
                           ingresos=total_ingresos,
                           gastos=total_gastos,
                           ganancia=ganancia,
                           movimientos=movimientos)


# ============================
# RESUMEN DIARIO
# ============================
@app.route("/resumen")
def resumen():
    hoy = str(date.today())

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(monto) FROM contabilidad WHERE tipo='Ingreso' AND fecha=?", (hoy,))
    ingresos = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(monto) FROM contabilidad WHERE tipo='Gasto' AND fecha=?", (hoy,))
    gastos = cursor.fetchone()[0] or 0

    ganancia = ingresos - gastos

    # FORMATO PRO
    ingresos = round(ingresos, 2)
    gastos = round(gastos, 2)
    ganancia = round(ganancia, 2)

    conn.close()

    return render_template("resumen.html",
                           ingresos=ingresos,
                           gastos=gastos,
                           ganancia=ganancia,
                           fecha=hoy)


# ============================
# RUN SERVER
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
