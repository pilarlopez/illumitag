#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to run some stuff on Inga's experiment.
"""

# Modules #
import illumitag, shutil
from plumbing.autopaths import DirectoryPath
from tqdm import tqdm

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
pool.create_raw_samples()
make_raw_zip_bundle(cluster)