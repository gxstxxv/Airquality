import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import seaborn as sns

df = pd.read_csv('./frames/daily_mean_pm2_and_sum_prec.csv')

pearson_corr, pearson_p = pearsonr(
    df['daily_mean_pm25'], df['daily_total_prec'])
spearman_corr, spearman_p = spearmanr(
    df['daily_mean_pm25'], df['daily_total_prec'])

print(f"Pearson-Korrelation: {pearson_corr:.3f} (p-Wert: {pearson_p:.3f})")
print(f"Spearman-Korrelation: {spearman_corr:.3f} (p-Wert: {spearman_p:.3f})")

df['pm25_cat'] = pd.cut(df['daily_mean_pm25'],
                        bins=[0, 5, 15, float('inf')],
                        labels=['gut (≤5)', 'mäßig (5-15)', 'schlecht (>15)'])

df['prec_cat'] = pd.cut(df['daily_total_prec'],
                        bins=[0, 0.1, 7, float('inf')],
                        labels=['trocken (0)', 'mäßig (0.1-7)', 'stark (>7)'])

contingency_table = pd.crosstab(df['pm25_cat'], df['prec_cat'])
print("\nKreuztabelle:")
print(contingency_table)

plt.figure(figsize=(8, 6))
sns.heatmap(contingency_table, annot=True, fmt='d', cmap='YlOrRd',
            cbar_kws={'label': 'Anzahl Tage'})
plt.title('PM2.5 vs. Niederschlag\n(WHO-Kategorien)')
plt.ylabel('PM₂.₅ Kategorien (µg/m³)')
plt.xlabel('Niederschlag Kategorien (mm/Tag)')
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 6))
contingency_pct = contingency_table.div(
    contingency_table.sum(axis=1), axis=0) * 100
sns.heatmap(contingency_pct, annot=True, fmt='.1f', cmap='YlOrRd',
            cbar_kws={'label': 'Prozent innerhalb PM2.5-Kategorie'})
plt.title('PM2.5 vs. Niederschlag (Prozentuale Verteilung)\n(WHO-Kategorien)')
plt.ylabel('PM₂.₅ Kategorien (µg/m³)')
plt.xlabel('Niederschlag Kategorien (mm/Tag)')
plt.tight_layout()
plt.show()
