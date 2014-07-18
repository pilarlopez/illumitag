#!/usr/bin/env python2

"""
A script to convert some tsv files
to our json files.
"""

# Modules #
import pandas

###############################################################################
# Load data #
df = pandas.io.parsers.read_csv('new_data.tsv', sep='\t', index_col=0, encoding='utf-8', dtype=str)

# Iterate #
for row in df:
    print row