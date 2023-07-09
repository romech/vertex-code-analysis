import pandas as pd

df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

for index, row in df.iterrows():
    df.loc[index, 'z'] = row['x'] * row['y']
