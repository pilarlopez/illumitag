#!/usr/bin/env python2

"""
A script to make some graphs for the soda project.
"""

# Modules #
import illumitag, seaborn
from matplotlib import pyplot
from matplotlib.patches import Patch

# Constants #
project = illumitag.projects['ice']
project.cluster.load()
norm_table = project.cluster.otu_uparse.taxonomy_silva.otu_table_norm
assignments = project.cluster.otu_uparse.taxonomy_silva.assignments

# Graphs #
width  = 12.0
height = 7.0
bottom = 0.5
top    = 0.93
left   = 0.08
right  = 0.98

# Colors #
cool_colors = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71",
               "#FCD124", "#5F0061", "#FBBEBA", "#AAC2F6", "#606925", "#469A55",
               "#ABD8B2", "#B4B1ED", "#613162", "#76C3E5", "#F05575", "#48CBD1"]

###############################################################################
def top5_otus(sample):
    row = norm_table.loc[sample.short_name]
    row.sort(inplace=True, ascending=False)
    return set(row[0:5].index)

###############################################################################
def make_sandwich(lake):
    # Get data #
    otus = list(set.union(*(top5_otus(s) for s in lake)))
    names = [s.short_name for s in lake]
    depths = [s.info['depth'][0] for s in lake]
    # Get sub matrix and order it #
    abund = norm_table[otus].loc[names]
    abund = abund.reindex_axis(abund.sum().sort(inplace=False, ascending=False).index, axis=1)
    # Make graph #
    fig, axes = pyplot.subplots()
    axes.stackplot(depths, abund.T, colors=cool_colors)
    # Adjust #
    fig.set_figwidth(width)
    fig.set_figheight(height)
    fig.subplots_adjust(hspace=0.0, bottom=bottom, top=top, left=left, right=right)
    axes.set_xlim(min(depths), max(depths))
    # Add legend #
    label = lambda i: ', '.join(assignments[otus[i]]) + " (" + otus[i] + ')'
    handles = [Patch(color=cool_colors[i], label=label(i)) for i in range(len(otus))]
    axes.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    # Text
    axes.set_title('Relative abundance of the top OTUs for lake "%s"' % lake.name)
    axes.set_xlabel('Depth in meters')
    axes.set_ylabel('Relative abundance in that depth')
    # Style #
    seaborn.set(font="serif")
    seaborn.set_style("whitegrid")
    seaborn.set_style("ticks")
    seaborn.despine(offset=10, trim=True);
    # Save #
    fig.savefig(lake.name + ".pdf")
    pyplot.close(fig)

###############################################################################
lake_names = ('bt', 'rl', 'lb', 'kt', 'sb')
for name in lake_names:
    samples = [s for s in illumitag.runs[10] if s.group == 'ice-%s' % name]
    lake = illumitag.clustering.Cluster(samples, 'ice-%s' % name)
    exec("%s = lake" % name)
    make_sandwich(lake)