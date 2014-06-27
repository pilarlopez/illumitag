#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to run the clustering analyses for Silke's experiment.
"""

# Future #
from __future__ import division

# Don't run it #
import sys
sys.exit("Copy paste the commands you want in ipython, don't run this script.")

# Modules #
import illumitag, pandas

###############################################################################
# Get the cluster #
cluster = illumitag.clustering.favorites.anna

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
cluster.otu_uparse.seqenv.run(threshold=1.0)

# Run seqenv via SLURM #
cluster.run(steps=[{'otu_uparse.seqenv.run': dict(threads=False, threshold=1.0, N=3000)}])
cluster.run_slurm(steps=[{'otu_uparse.seqenv.run': dict(threads=False, threshold=1.0, N=3000)}], time="1-00:00:00")

# Check some matrix multiplications #
otu_vs_envo = cluster.otu_uparse.seqenv.base_dir + "centers_N1000_blast_F_ENVO_OTUs_labels.csv"
otu_vs_envo = pandas.io.parsers.read_csv(otu_vs_envo, sep=',', index_col=0, encoding='utf-8')
otu_vs_samples = cluster.otu_uparse.seqenv.base_dir + "abundances.csv"
otu_vs_samples = pandas.io.parsers.read_csv(otu_vs_samples, sep=',', index_col=0, encoding='utf-8')
otu_vs_samples = otu_vs_samples.loc[otu_vs_envo.index]
otu_vs_samples = otu_vs_samples.transpose()
result_us = otu_vs_samples.dot(otu_vs_envo)
result_them = cluster.otu_uparse.seqenv.base_dir + "centers_N1000_blast_F_ENVO_samples_labels.csv"
result_them = pandas.io.parsers.read_csv(result_them, sep=',', index_col=0, encoding='utf-8')
result_them.sum(axis=1)
cluster.otu_uparse.taxonomy_silva.otu_table