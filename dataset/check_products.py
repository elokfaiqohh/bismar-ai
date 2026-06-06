import pandas as pd

df = pd.read_csv('Data2.csv')
products = df['nama_produk'].unique()
print(f'Unique products in Data2.csv: {len(products)}')
print('\nAll products:')
for p in products:
    print(f'  - {p}')
