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

# Create BioSamples #
from illumitag.helper.sra import MakeSpreadsheet
make_tsv = MakeSpreadsheet(cluster)
make_tsv.write_bio_tsv()

# Submit to SRA #
make_tsv.write_sra_tsv()

# The pyro samples #
cluster_pyro = illumitag.clustering.Cluster(samples_pyro, 'soda_model_lakes_pyro')
make_tsv_pyro = MakeSpreadsheet(cluster_pyro)
make_tsv_pyro.platform                = "LS454"
make_tsv_pyro.instrument_model        = "454 GS FLX Titanium"
make_tsv_pyro.forward_read_length     = "500"
make_tsv_pyro.reverse_read_length     = "500"
make_tsv_pyro.forward_filetype        = "sff"
make_tsv_pyro.reverse_filetype        = "sff"
make_tsv_pyro.write_sra_tsv()

# Copy files
#cp /My\ Folders/PHD/Server/Uppmax_home/ILLUMITAG/views/clusters/soda_model_lakes_pyro/sra/sra_submission.tsv /My\ Folders/PHD/-ILLUMITAQ-/Other/SRA\ spreadsheet/soda/2.tsv
#cp /My\ Folders/PHD/Server/Uppmax_home/ILLUMITAG/views/clusters/soda_model_lakes/sra/sra_submission.tsv /My\ Folders/PHD/-ILLUMITAQ-/Other/SRA\ spreadsheet/soda/1.tsv