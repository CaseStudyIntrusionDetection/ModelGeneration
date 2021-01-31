import os

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from src.transformation.ZAPIDTransformer import ZAPIDTransformer

def create_id_count_plot(df, filename, proj_root, path_to_plot_dir='', figsize=(12, 8), height_ratios=[3,1]):
    """Creates a count bar plot for attack dypes.
    Saves the plot, if `path_to_plot_dir` string is not empty.

    Args:
        df (pd.DataFrame): structured df dataframe, preprocessed with DataLoaderJSON
        filename (str): filename (just needed for plot title)
        proj_root (str): path to project root
        path_to_plot_dir (str, optional): path to plot directory (from `proj_root`). Defaults to ''.
        figsize (tuple, optional): matplotlib figure size tuple. Defaults to (12, 8).
    """
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(2,2, figure=fig, height_ratios=height_ratios, width_ratios=[2,1])

    ax_main = fig.add_subplot(gs[0, :])
    ax_table1 = fig.add_subplot(gs[1, 0])
    ax_table1.axis("off")
    ax_table2 = fig.add_subplot(gs[1, 1])
    ax_table2.axis("off")

    ax = sns.countplot(x="original-zap-id", data=df, ax=ax_main)
    for p in ax.patches:
        ax.annotate(format(p.get_height(), 'd'),
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center',
                    size=10,
                    xytext=(0, 5),
                    textcoords='offset points')
    ax.set_xlabel("Attack Type")
    ax.set_ylabel("Count")
    ax.set_title(f"Attack Type Counts for {filename}")
    ax.set_xticklabels(labels=ax.get_xticklabels(), rotation=45)

    zapper = ZAPIDTransformer(proj_root)
    
    # Table 1 (counts per ID)
    col_labels = ['counts', 'perc']
    row_labels = [
        f"{x.get_text()} - {zapper.id_to_rule(x.get_text())} " for x in ax.get_xticklabels()]
    counts = [h.get_height() for h in ax.patches]
    percentages = [round(c / sum(counts), 2) for c in counts]
    table_vals = [[c,p] for c, p in zip(counts, percentages)]
    table1 = ax_table1.table(cellText=table_vals,
                          rowLabels=row_labels,
                          colLabels=col_labels,
                          colWidths= [0.2, 0.1, 0.05],
                          #loc='upper center',
                          loc='center right',
                          colLoc="right",
                          edges='horizontal'
                          )

    # Table 2 (counts for attack / benign)
    col_labels = ['counts', 'perc']
    row_labels = ['attack', 'benign']
    counts = [df.shape[0] - (df['label'] == 'no zap id').sum(),
                    (df['label'] == 'no zap id').sum() ]
    percentages = [round(c / sum(counts), 2) for c in counts]
    table_vals = [[c,p] for c, p in zip(counts, percentages)]
    table2 = ax_table2.table(
        cellText=table_vals,
        colWidths= [0.4, 0.15, 0.15],
        rowLabels=row_labels,
        colLabels=col_labels,
        #loc='lower center',
        loc='center',
        colLoc="right",
        edges='horizontal'
    )
    
    fig.tight_layout()
    if path_to_plot_dir != "":
        filename = os.path.splitext(os.path.basename(filename))[0] + ".png"
        filepath = os.path.join(path_to_plot_dir, filename)
        print(f"Saving plot as '{filepath}'")
        plt.savefig(filepath, bbox_inches='tight')
