import pandas as pd

def generar_excel_coloreado(df, output):
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="RESULTADOS")

    wb = writer.book
    ws = writer.sheets["RESULTADOS"]

    azul = wb.add_format({'font_color': 'blue'})
    rojo = wb.add_format({'font_color': 'red'})

    col = df.columns.get_loc("EstadoDescarga")

    for row, estado in enumerate(df["EstadoDescarga"], start=1):
        ws.write(row, col, estado, azul if estado == "OK" else rojo)

    writer.close()
