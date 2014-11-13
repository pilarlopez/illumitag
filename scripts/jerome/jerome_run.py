#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to run the clustering analyses for Eva's experiment.
"""

# Future #
from __future__ import division

# Don't run it #
import sys
sys.exit("Copy paste the commands you want in ipython, don't run this script.")

# Modules #
import illumitag

###############################################################################
# Get the cluster #
cluster = illumitag.clustering.favorites.jerome.load()

# Run UPARSE with different threshold #
cluster.otu_uparse.run(threshold=1.0)

# Other stuff #
cluster.otu_uparse.taxonomy_silva.assign()
cluster.otu_uparse.taxonomy_silva.make_otu_table()
cluster.otu_uparse.taxonomy_silva.make_otu_table_norm()
cluster.otu_uparse.taxonomy_silva.make_plots()
cluster.otu_uparse.taxonomy_silva.stats.nmds.run()
cluster.otu_uparse.taxonomy_silva.make_filtered_centers()

# Run seqenv #
cluster.otu_uparse.seqenv.threshold = 1.0
cluster.otu_uparse.seqenv.N = 5000
cluster.otu_uparse.seqenv.run()

# Run seqenv via SLURM #
cluster.run(steps=[{'otu_uparse.seqenv.run': {}}])
cluster.run_slurm(steps=[{'otu_uparse.seqenv.run': {}}], time="04:00:00")