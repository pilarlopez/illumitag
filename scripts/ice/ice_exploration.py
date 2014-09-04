#!/usr/bin/env python2

"""
A script to make some graphs for the soda project.
"""

# Modules #
import illumitag

###############################################################################
project = illumitag.projects['ice']
project.cluster.load()
norm_table = project.cluster.otu_uparse.taxonomy_silva.otu_table_norm

def top5(sample):
    row = norm_table.loc[sample.short_name]
    row.sort(inplace=True, ascending=False)
    return set(row[0:5].index)

def make_sandwich(lake):
    otus = sum(top5(s) for s in lake)
    names = [s.short_name for s in lake]
    abundances = norm_table[otus].loc[names]
    depths = [s.info['depth'] for s in lake]
    plot(abundances, depths)

lake_names = ('bt', 'rl', 'lb', 'kt', 'sb')
for name in lake_names:
    # Make a cluster #
    samples = [s for s in illumitag.runs[10] if s.group == 'ice-%s' % name]
    lake = illumitag.clustering.Cluster(samples, 'ice-%s' % name)
    exec("%s = lake" % lake)
