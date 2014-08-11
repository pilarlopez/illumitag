#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to run some of the new data we got.
"""

# Future #
from __future__ import division

# Don't run it #
import sys
sys.exit("Copy paste the commands you want in ipython, don't run this script.")

# Modules #
import illumitag

###############################################################################
# Sample #
s = illumitag.runs[10][1]
s.run_fastqc()
s.join()
s.check_noalign_counts()
s.assembled.length_dist_graph.plot()
s.assembled.fastqc()
s.assembled.dont_flip_reads()
s.assembled.make_primer_groups()
s.assembled.discard_reads_with_n()
s.assembled.quality_filter()
s.assembled.length_filter()
s.process()
for g in s.diversity.graphs: g.plot()
s.report.generate()
s.report.web_export()

# Project #
p = illumitag.projects['allinen']
p.cluster.combine_reads()
p.cluster.reads.graphs[1].plot()
p.cluster.otus.run()
p.cluster.otus.taxonomy.assign()
p.cluster.otus.taxonomy.make_otu_table()
p.cluster.otus.taxonomy.make_otu_table_norm()
p.cluster.otus.taxonomy.make_plots()
p.cluster.otus.taxonomy.stats.nmds.run()
p.cluster.otus.taxonomy.make_filtered_centers()
p.cluster.otus.taxonomy.comp_phyla.make_taxa_table()
p.cluster.otus.taxonomy.comp_phyla.make_plots()
p.cluster.otus.taxonomy.comp_phyla.stats.nmds.run()
p.cluster.otus.taxonomy.comp_tips.make_taxa_table()
p.cluster.otus.taxonomy.comp_tips.make_plots()
p.cluster.otus.taxonomy.comp_tips.stats.nmds.run()
#p.cluster.otus.taxonomy.stats.unifrac.run()
p.cluster.report.generate()
p.cluster.report.web_export()

###############################################################################
# All #
samples = illumitag.runs[10][:96]
def first(s):
    print s
    s.run_fastqc()
    s.join()
    s.check_noalign_counts()
    s.assembled.length_dist_graph.plot()
    s.assembled.fastqc()
    s.assembled.dont_flip_reads()
    s.assembled.make_primer_groups()
    s.assembled.discard_reads_with_n()
    s.assembled.quality_filter()
    s.assembled.length_filter()
    s.process()
for s in samples: first(s)

p = illumitag.projects['alinen']
p = illumitag.projects['mekko']
p = illumitag.projects['kivu']
p = illumitag.projects['ice']
p = illumitag.projects['klubban']

def second(s):
    print s
    for g in s.diversity.graphs: g.plot()
    s.report.generate()
    s.report.web_export()
for s in samples: second(s)

###############################################################################
# Unfiltered OTU table #
p.cluster.otus.cluster_counts_table.to_csv(p.cluster.otus.base_dir + 'unfiltered_otus.tsv', sep='\t', float_format='%.5g')
