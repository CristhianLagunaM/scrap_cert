import pandas as pd

def cargar_excel(path_excel):
    """
    Carga el archivo Excel, limpia los datos y devuelve el DF unificado
    con encabezados reales desde la fila 4.
    """

    # Cargar sin encabezados
    df_raw = pd.read_excel(path_excel, header=None)

    # La fila 3 contiene los nombres reales de las columnas
    new_header = df_raw.iloc[3]
    df = df_raw[4:].copy()
    df.columns = new_header
    df = df.reset_index(drop=True)

    # Normalizaciones
    df["Tipo Inscripcion"] = df["Tipo Inscripcion"].astype(str).str.upper().str.strip()

    df["Cred"] = (
        df["Cred"]
        .astype(str)
        .str.replace(" ", "")
        .str.strip()
    )

    df["Nro Iden"] = (
        df["Nro Iden"]
        .astype(str)
        .str.replace(" ", "")
        .str.strip()
    )

    return df


def cargar_y_dividir(path_excel):
    """
    Usa cargar_excel() y devuelve:
      df_minorias, df_indigenas
    """

    df = cargar_excel(path_excel)

    df_minorias = df[df["Tipo Inscripcion"].str.contains("MINORIAS", case=False, na=False)].copy()
    df_indigenas = df[df["Tipo Inscripcion"].str.contains("INDIGENAS", case=False, na=False)].copy()

    return df_minorias, df_indigenas
