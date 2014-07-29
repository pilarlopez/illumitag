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
# Check bad samples #
s = illumitag.runs[10][-1]
s.fwd.indices_counter.most_common(100)

# Check good samples #
s = illumitag.runs[10][26]
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
s.report.generate()
s.process()

# Project #
p = illumitag.projects['kivu']
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
p.cluster.report.generate()

# Run all #
for s in samples:
    print s