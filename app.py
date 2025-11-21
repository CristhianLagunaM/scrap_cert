# app.py
import os
import sys
import asyncio
from flask import Flask, request, render_template, send_from_directory
from utils.loader import cargar_excel
from utils.excel import generar_excel_coloreado
from scrapers.scraper_minorias import scrap_minorias
from scrapers.scraper_indigenas import scrap_indigenas

# Detectar ruta real del programa (soporta EXE)
if getattr(sys, "frozen", False):
    APP_ROOT = os.path.dirname(sys.executable)
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
OUTPUT_FOLDER = os.path.join(APP_ROOT, "salidas")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------------------
# Descarga
# ------------------------------
@app.route("/salidas/<path:filename>")
def descargar_archivo(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

# ------------------------------
# Home
# ------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# ------------------------------
# Procesar archivo
# ------------------------------
@app.route("/procesar", methods=["POST"])
def procesar():
    if "archivo" not in request.files:
        return render_template("index.html", status="❌ No se envió archivo.")

    f = request.files["archivo"]
    if f.filename == "":
        return render_template("index.html", status="❌ Archivo inválido.")

    path_excel = os.path.join(app.config["UPLOAD_FOLDER"], "entrada.xlsx")
    f.save(path_excel)

    try:
        detalles = asyncio.run(procesar_async(path_excel))
        return render_template("index.html", status="✔ Proceso finalizado", detalles=detalles)
    except Exception as e:
        return render_template("index.html", status=f"❌ Error: {e}")

# ------------------------------
# Lógica async
# ------------------------------
async def procesar_async(path_excel):
    df = cargar_excel(path_excel)

    df_min = df[df["Tipo Inscripcion"].str.contains("MINORIAS", na=False)].copy()
    df_ind = df[df["Tipo Inscripcion"].str.contains("INDIGENAS", na=False)].copy()

    detalles = []

    # MINORIAS
    if not df_min.empty:
        df_min_r = await scrap_minorias(df_min, OUTPUT_FOLDER)
        out_min = os.path.join(OUTPUT_FOLDER, "resultado_minorias.xlsx")
        generar_excel_coloreado(df_min_r, out_min)
        detalles.append("✔ MINORÍAS procesado con éxito.")
    else:
        detalles.append("ℹ No hay registros MINORÍAS.")

    # INDÍGENAS
    if not df_ind.empty:
        df_ind_r = await scrap_indigenas(df_ind, OUTPUT_FOLDER)
        out_ind = os.path.join(OUTPUT_FOLDER, "resultado_indigenas.xlsx")
        generar_excel_coloreado(df_ind_r, out_ind)
        detalles.append("✔ INDÍGENAS procesado con éxito.")
    else:
        detalles.append("ℹ No hay registros INDÍGENAS.")

    return detalles

# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
