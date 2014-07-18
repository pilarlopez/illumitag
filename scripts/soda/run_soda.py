#!/usr/bin/env python2

"""
A script to run the clustering analyses some of the soda samples.
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
samples_pyro = [s for s in illumitag.pyrosamples if s.run_num==9999]
samples = [s.mate for s in samples_pyro]
cluster = illumitag.clustering.Cluster(samples, 'soda_model_lakes')

# Upload raw samples for SRA #
pool = illumitag.runs[3][7]
pool.create_raw_samples()
for s in samples: s.sra.upload_to_sra()
for s in samples_pyro: s.sra.upload_to_sra()

# Submit to SRA #
from illumitag.helper.sra import MakeSpreadsheet
make_tsv = MakeSpreadsheet(cluster)
make_tsv.write_bio_tsv()
make_tsv.bioproject_accession = "PRJNA255371"
make_tsv.write_sra_tsv()


cluster = illumitag.clustering.favorites.soda; from illumitag.helper.sra import MakeSpreadsheet; make_tsv = MakeSpreadsheet(cluster); make_tsv.write_bio_tsv()