#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to run some stuff on Inga's experiment.
"""

# Modules #
import illumitag, shutil
from illumitag.common.autopaths import DirectoryPath
from tqdm import tqdm

###############################################################################
def generate_raw_samples(pool):
    """Sort the sequences in different files according to their barcode
    before any other quality filtering such as read joining."""
    if not pool.loaded: pool.load()
    for sample in pool.samples: sample.raw.create()
    for r in tqdm(pool.good_barcodes.parse_barcodes()): r.first.sample.raw.add_pair(r)
    for sample in pool.samples: sample.raw.close()

###############################################################################
def make_raw_zip_bundle(cluster):
    """Zip all the raw samples files in one file"""
    result_dir = DirectoryPath(cluster.base_dir + "raw_reads")
    result_dir.remove()
    result_dir.create()
    for sample in tqdm(cluster.samples):
        subdir = DirectoryPath(result_dir + sample.short_name)
        subdir.create()
        shutil.copy(sample.raw.fwd, subdir)
        shutil.copy(sample.raw.rev, subdir)
    result_dir.zip(keep_orig=False)

###############################################################################
pool = illumitag.runs[3][6]
cluster = illumitag.clustering.favorites.inga
generate_raw_samples(pool)
make_raw_zip_bundle(cluster)