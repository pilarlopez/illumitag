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
s.fwd.indices_counter

# Check good samples #
s = illumitag.runs[10][0]

# Raw data #
s.fastqc