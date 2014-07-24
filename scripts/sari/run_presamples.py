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
# Get vars #
#proj = illumitag.projects['evaluation']
#pools = proj.pools
#samples = [s for pool in proj for s in pool.samples]
#cluster = illumitag.clustering.favorites.evaluation

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

# Raw data #
s.fastqc