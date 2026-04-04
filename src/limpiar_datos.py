import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_master_2010_2026.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_limpio.csv")

COLUMNAS_OBJETIVO = [
    'ATP', 'LOCATION', 'TOURNAMENT', 'DATE', 'SERIES', 'COURT', 'SURFACE', 'ROUND', 
    'BEST OF', 'WINNER', 'LOSER', 'WRANK', 'LRANK', 'WSETS', 'LSETS', 'COMMENT',
    'B365W', 'B365L', 'PSW', 'PSL'
]

def limpiar():
    if not os.path.exists(INPUT_PATH):
        print("Error: Ejecuta primero unificar_datos.py")
        return

    df = pd.read_csv(INPUT_PATH, low_memory=False)
    df.columns = [c.upper().strip() for c in df.columns]

    # 1. Filtrar columnas
    cols_presentes = [c for c in COLUMNAS_OBJETIVO if c in df.columns]
    df = df[cols_presentes]

    # 2. LIMPIEZA DE DECIMALES (Crucial)
    # Reemplazamos la coma por punto y convertimos a número
    for col in ['B365W', 'B365L', 'PSW', 'PSL']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Formateo de fechas
    df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')
    
    # 4. Eliminar filas sin cuotas o fechas inválidas
    antes = len(df)
    df = df.dropna(subset=['DATE'])
    # Solo nos sirven partidos donde al menos tengamos las cuotas de Bet365
    df = df.dropna(subset=['B365W', 'B365L'])
    despues = len(df)

    # 5. Ordenar cronológicamente
    df = df.sort_values('DATE')

    df.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 30)
    print(f"Limpieza completada con éxito.")
    print(f"Partidos recuperados: {despues} de {antes}")
    print(f"Tipos de datos B365W: {df['B365W'].dtype}") # Debe decir float64
    print(f"Archivo guardado en: {os.path.abspath(OUTPUT_PATH)}")

if __name__ == "__main__":
    limpiar()