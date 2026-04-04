import pandas as pd
import glob
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW_DIR = os.path.join(BASE_DIR, "..", "data", "raw")
all_files = glob.glob(os.path.join(DATA_RAW_DIR, "*.csv"))

df_list = []
for filename in all_files:
    try:
        # sep=None con engine='python' detecta automáticamente si es , o ;
        df = pd.read_csv(filename, sep=None, engine='python', encoding='latin1')
        df_list.append(df)
        print(f"Cargado correctamente: {os.path.basename(filename)}")
    except Exception as e:
        print(f"Error en {filename}: {e}")

if df_list:
    full_df = pd.concat(df_list, axis=0, ignore_index=True)
    output_path = os.path.join(BASE_DIR, "..", "data", "processed", "atp_master_2010_2026.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Guardamos el maestro SIEMPRE con comas para estandarizar
    full_df.to_csv(output_path, index=False)
    print(f"\nÉXITO: Dataset maestro creado con {len(full_df)} filas.")