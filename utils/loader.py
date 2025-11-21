import pandas as pd

def cargar_excel(path_excel):
    """
    Carga y normaliza el archivo Excel.
    - Toma encabezados reales de la fila 4 (índice 3).
    - Limpia espacios y normaliza tipos de documento.
    - Garantiza que las columnas críticas existan.
    """

    # Leer Excel sin encabezado original
    df_raw = pd.read_excel(path_excel, header=None)

    # Validar tamaño mínimo esperado
    if df_raw.shape[0] < 5:
        raise ValueError("El archivo es demasiado pequeño o no tiene el formato esperado.")

    # La fila 3 tiene los nombres reales de las columnas
    new_header = df_raw.iloc[3]

    df = df_raw[4:].copy()
    df.columns = new_header
    df = df.reset_index(drop=True)

    # Normalización útil en contenedores
    def clean(col):
        return (
            col.astype(str)
               .str.replace(r"\s+", "", regex=True)
               .str.strip()
               .str.upper()
        )

    # Validar columnas necesarias
    required_cols = ["Tipo Inscripcion", "Cred", "Nro Iden"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"❌ Falta la columna obligatoria: {col}")

    # Normalizaciones
    df["Tipo Inscripcion"] = clean(df["Tipo Inscripcion"])
    df["Cred"]             = clean(df["Cred"])
    df["Nro Iden"]         = clean(df["Nro Iden"])

    return df


def cargar_y_dividir(path_excel):
    """
    Devuelve DataFrames separados por tipo de inscripción
    """

    df = cargar_excel(path_excel)

    df_minorias = df[df["Tipo Inscripcion"].str.contains("MINORIAS", na=False)].copy()
    df_indigenas = df[df["Tipo Inscripcion"].str.contains("INDIGENAS", na=False)].copy()

    return df_minorias, df_indigenas
