import sys
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


def find_pareto_frontier(df, x_col, y_col):
    df_sorted = df.sort_values(by=[x_col, y_col], ascending=[False, False])

    pareto_front = []
    max_y = -np.inf

    for _, row in df_sorted.iterrows():
        if row[y_col] >= max_y:
            pareto_front.append(row)
            max_y = row[y_col]

    return pd.DataFrame(pareto_front)


def main(fname):
    df = pd.read_csv(fname)
    df.cspeed /= 2**20

    index_tuned = df.desc.str.contains('\|')
    df_defaults = df[~index_tuned]
    df_tuned = df[index_tuned]
    df_pareto = find_pareto_frontier(df_tuned, 'cr', 'cspeed')

    plt.figure()
    for _, row in df_defaults.iterrows():
        plt.plot(row.cspeed, row.cr, '*', label=row.desc)
    plt.plot(df_tuned.cspeed, df_tuned.cr, 'ko')
    for _, row in df_pareto.iterrows():
        plt.plot(row.cspeed, row.cr, '.', label=row.desc)
    plt.legend()
    plt.xlabel('Compression speed, MB/s')
    plt.ylabel('CR')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} CSV_FILE')
        exit()
    main(Path(sys.argv[1]))
