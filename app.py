# app.py
import os
import asyncio
from flask import Flask, request, render_template, send_from_directory
from utils.loader import cargar_excel
from utils.excel import generar_excel_coloreado
from scrapers.scraper_minorias import scrap_minorias
from scrapers.scraper_indigenas import scrap_indigenas

# --------------------------------------------------------------
# Carpetas dentro del contenedor Railway
# --------------------------------------------------------------
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
OUTPUT_FOLDER = os.path.join(APP_ROOT, "salidas")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --------------------------------------------------------------
# DESCARGA DIRECTA DE ARCHIVOS GENERADOS
# --------------------------------------------------------------
@app.route("/salidas/<path:filename>")
def descargar_archivo(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

# --------------------------------------------------------------
# HOME (Frontend)
# --------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# --------------------------------------------------------------
# PROCESAR ARCHIVO (Endpoint principal)
# --------------------------------------------------------------
@app.route("/procesar", methods=["POST"])
def procesar():
    if "archivo" not in request.files:
        return render_template("index.html", status="❌ No se envió archivo.")

    f = request.files["archivo"]
    if f.filename == "":
        return render_template("index.html", status="❌ Archivo inválido.")

    path_excel = os.path.join(UPLOAD_FOLDER, "entrada.xlsx")
    f.save(path_excel)

    try:
        detalles = asyncio.run(procesar_async(path_excel))
        return render_template(
            "index.html",
            status="✔ Proceso finalizado",
            detalles=detalles
        )
    except Exception as e:
        return render_template("index.html", status=f"❌ Error: {e}")

# --------------------------------------------------------------
# PROCESAMIENTO ASÍNCRONO REAL
# --------------------------------------------------------------
async def procesar_async(path_excel):

    df = cargar_excel(path_excel)

    df_min = df[df["Tipo Inscripcion"].str.contains("MINORIAS", na=False)].copy()
    df_ind = df[df["Tipo Inscripcion"].str.contains("INDIGENAS", na=False)].copy()

    detalles = []

    # ----------- MINORÍAS -----------
    if not df_min.empty:
        df_min_r = await scrap_minorias(df_min, OUTPUT_FOLDER)
        path_min = os.path.join(OUTPUT_FOLDER, "resultado_minorias.xlsx")
        generar_excel_coloreado(df_min_r, path_min)
        detalles.append("✔ MINORÍAS procesado con éxito.")
    else:
        detalles.append("ℹ No hay registros MINORÍAS.")

    # ----------- INDÍGENAS -----------
    if not df_ind.empty:
        df_ind_r = await scrap_indigenas(df_ind, OUTPUT_FOLDER)
        path_ind = os.path.join(OUTPUT_FOLDER, "resultado_indigenas.xlsx")
        generar_excel_coloreado(df_ind_r, path_ind)
        detalles.append("✔ INDÍGENAS procesado con éxito.")
    else:
        detalles.append("ℹ No hay registros INDÍGENAS.")

    return detalles


# --------------------------------------------------------------
# RUN (Railway usa PORT env automáticamente)
# --------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

