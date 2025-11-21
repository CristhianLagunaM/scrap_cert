import pandas as pd

def generar_excel_coloreado(df, output):
    """
    Genera un Excel con la columna 'EstadoDescarga' coloreada:
    - OK     → azul
    - ERROR  → rojo
    """

    # Validación segura
    if "EstadoDescarga" not in df.columns:
        raise ValueError("❌ La columna 'EstadoDescarga' no existe en el DataFrame.")

    # Usar context manager (mucho mejor en Docker/Railway)
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="RESULTADOS")

        wb = writer.book
        ws = writer.sheets["RESULTADOS"]

        azul = wb.add_format({'font_color': 'blue'})
        rojo = wb.add_format({'font_color': 'red'})

        col = df.columns.get_loc("EstadoDescarga")

        # Pintar filas
        for row, estado in enumerate(df["EstadoDescarga"], start=1):
            fmt = azul if str(estado).upper() == "OK" else rojo
            ws.write(row, col, estado, fmt)
