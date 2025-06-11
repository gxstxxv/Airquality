from scipy.stats import chi2_contingency
import pandas as pd
import numpy as np

df = pd.read_csv('./frames/daily_mean_pm2_and_sum_prec.csv')

df['pm25_category'] = pd.cut(df['daily_mean_pm25'],
                             bins=3,
                             labels=['niedrig', 'mittel', 'hoch'])

df['prec_category'] = pd.cut(df['daily_total_prec'],
                             bins=[0, 0.1, 5, float('inf')],
                             labels=['trocken', 'leicht', 'stark'])

crosstab = pd.crosstab(df['pm25_category'], df['prec_category'])
print(crosstab)

chi2, p_value, dof, expected = chi2_contingency(crosstab)

n = crosstab.sum().sum()
contingency_coeff = np.sqrt(chi2 / (chi2 + n))
corrected_contingency_coeff = contingency_coeff / \
    np.sqrt((min(crosstab.shape) - 1) / min(crosstab.shape))

print(f"Chi-Quadrat: {chi2:.3f} (p-Wert: {p_value:.3f})")
print(f"Kontingenzkoeffizient: {contingency_coeff:.3f}")
print(f"Korrigierter Kontingenzkoeffizient: {corrected_contingency_coeff:.3f}")
