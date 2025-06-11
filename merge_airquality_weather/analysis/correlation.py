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

# Pearson-Korrelation: -0.145 (p-Wert: 0.000)
# Spearman-Korrelation: -0.246 (p-Wert: 0.000)

df['prec_cat'] = pd.cut(df['daily_total_prec'],
                        bins=[0, 0.1, 1, 5, 10, float('inf')],
                        labels=[
                        '0.0',
                        '0.1-1.0',
                        '1.0-5.0',
                        '5.0-10.0',
                        '>10.0',
                        ])

df['pm25_cat'] = pd.cut(df['daily_mean_pm25'],
                        bins=5,
                        labels=[
                        'very low',
                        'low',
                        'medium',
                        'high',
                        'very high',
                        ]
                        )

# PM₂.₅-Categories: very low: 0.0-12.9 µg/m³, low: 12.9-25.8 µg/m³,
# medium: 25.8-38.7 µg/m³, high: 38.7-51.6 µg/m³, very high: 51.6-64.5 µg/m³

contingency_table = pd.crosstab(df['pm25_cat'], df['prec_cat'])

plt.figure(figsize=(10, 6))
sns.heatmap(contingency_table, annot=True, fmt='d', cmap='Blues')
plt.title('Heatmap: Relationship between PM2.5' +
          ' Categories and Precipitation Categories')
plt.ylabel('PM₂.₅')
plt.xlabel('Precipitation (mm)')

plt.tight_layout()
plt.show()
