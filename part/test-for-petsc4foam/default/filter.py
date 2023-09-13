import pandas as pd


filename = 'petsc4foam.tsv'
columns = ['application', 'tutorial', 'parallel', 'time_foam', 'time_petsc']
key = 'petsc/foam'

df_all = pd \
    .read_csv(filename, sep='\t') \
    .dropna(how='any') \
    [columns]

print(df_all.to_markdown(index=False))

df_all[key] = df_all['time_petsc'] / df_all['time_foam']
df_top = df_all \
    [df_all[key] > 0] \
    .sort_values(key, ascending=True) \
    .reset_index(drop=True)

print(df_top.to_markdown(index=False))
