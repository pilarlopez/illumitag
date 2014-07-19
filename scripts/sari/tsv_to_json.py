#!/usr/bin/env python2

"""
A script to convert some tsv files
to our json files.
"""

# Modules #
import pandas

###############################################################################
template = """{
    "contacts": {
        "pi": {
            "name": "Alexander Eiler",
            "email": "alexander.eiler@ebc.uu.se"
        }
        "researcher_1": {
            "name": "Sari Peura",
            "email": "sari.peura@ebc.uu.se"
        },
        "researcher_2": {
            "name": "Lucas Sinclair",
            "email": "lucas.sinclair@ebc.uu.se"
        },
    },

    "uppmax_id":    "b2014083",
    "run_num":       10,
    "run_id":        "140610_M00629_0001_000000000-A8H0L",
    "sample_num":    {sample_num},
    "sample_id":     {sample_id},
    "forward_reads": {fwd_filename},
    "reverse_reads": {rev_filename},

    "project":       {project},
    "project_name":  {project_name},
    "sample":        {sample},
    "sample_name":   {sample_name},
    "group":         {group},

    "forward_mid":   {forward_mid},
    "forward_num":   {forward_num},
    "reverse_mid":   {reverse_mid},
    "reverse_num":   {reverse_num},
    "barcode_num":   {barcode_num},

    "primers": {
            "name":    "General bacteria primers",
            "sense":   "5' to 3'",
            "forward": {"name": "341F", "sequence": "NNNNCCTACGGGNGGCWGCAG"},
            "reverse": {"name": "805R", "sequence": "GACTACHVGGGTATCTAATCC"}
    }
}"""

###############################################################################
# Load data #
df = pandas.io.parsers.read_csv('new_data.tsv', sep='\t', index_col=0, encoding='utf-8', dtype=str)

# Iterate #
for row in df:
    print row