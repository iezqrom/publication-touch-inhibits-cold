# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plotting import (
    plotParams,
    prettifySpinesTicks,
    removeSpines,
    params_figure,
    colours
)

ultraviolet = "#654EA3"
driedmoss = "#CDBC7E"

plotParams(size=40)

base_path = '/home/iezquer/Nextcloud/coding/phd/publication-touch-inhibits-cold/'
path_summaries_staircase = f'{base_path}/data/staircase_summaries'

file_names = ['experiment', 'control', 'replication']
# %%
all_deltas = {}

for file_name in file_names:
    all_mean_deltas = pd.read_csv(f'{path_summaries_staircase}/df_{file_name}.csv')
    all_deltas[file_name] = list(all_mean_deltas['delta_mean'].values)
# %%
fig, ax = plt.subplots(1, 1, figsize=(10, 15))

for i, file_name in enumerate(file_names):
    x = np.random.normal(i+1, 0.03, size=len(all_deltas[file_name]))
    ax.scatter(
        list(x),
        all_deltas[file_name],
        s=params_figure["scatter_size"],
        color=colours["cold"],
    )

    mean_delta = np.mean(all_deltas[file_name])
    mean_pad = 0.3
    ax.plot(
        [i+(1-mean_pad), i+(1+mean_pad)],
        [mean_delta, mean_delta],
        color=colours["cold"],
        linewidth=params_figure["width_lines"],
    )

removeSpines(ax)
prettifySpinesTicks(ax)

# remove x ticks and labels
ax.set_xticks([1, 2, 3])
# change x labels
ax.set_xticklabels(['1', '2', '3'])
# set x title
ax.set_xlabel("Experiment")

pad = 0.5
ax.set_xlim([1-pad, 3+pad])

ax.set_ylim([-2, 0])
ax.set_yticks(np.arange(-2, 0.01, 0.2))

ax.set_ylabel("Percent-correct point\n\n(ΔT $^\circ$C)", linespacing=0.6)

plt.tight_layout()
path_figures = 'figures/figure_staircase'
plt.savefig(f'{base_path}/{path_figures}/all_staircases.png', dpi=300, transparent=True)

# %%
