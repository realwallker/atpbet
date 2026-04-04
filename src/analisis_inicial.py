import pandas as pd

df = pd.read_csv('../data/processed/atp_master_2010_2026.csv')

# Definir si el ganador real era el Underdog
# Si B365W > B365L, el ganador (W) tenía la cuota más alta
underdog_wins = df[df['B365W'] > df['B365L']]

total_matches = len(df)
wins = len(underdog_wins)
win_rate = (wins / total_matches) * 100

# Calcular ROI simple si apostaras $1 a cada underdog que ganó
inversion_total = total_matches
retorno_total = underdog_wins['B365W'].sum()
roi = ((retorno_total - inversion_total) / inversion_total) * 100

print(f"Análisis de Underdogs (2010-2026):")
print(f"Partidos totales: {total_matches}")
print(f"Victorias de Underdogs: {wins} ({win_rate:.2f}%)")
print(f"ROI Directo: {roi:.2f}%")