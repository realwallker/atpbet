import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "atp_limpio.csv")

def diagnosticar():
    df = pd.read_csv(FILE_PATH, low_memory=False)
    
    print(f"--- DIAGNÓSTICO DE DATOS ---")
    print(f"Total de filas en el archivo: {len(df)}")
    print(f"\nConteo de valores nulos por columna:")
    print(df[['B365W', 'B365L', 'PSW', 'PSL']].isnull().sum())
    
    print(f"\nPrimeras 5 filas de cuotas:")
    print(df[['B365W', 'B365L', 'WINNER', 'LOSER']].head())
    
    # Verificar si las columnas son numéricas
    print(f"\nTipos de datos:")
    print(df[['B365W', 'B365L']].dtypes)

if __name__ == "__main__":
    diagnosticar()