#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to convert some TSV files
to our JSON files.
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
df = pandas.io.parsers.read_csv('new_data.tsv', sep='\t', encoding='windows-1252', dtype=str)

# Correspondence #
corr = {'Added vol':            'lorem',
        'Barcode no.':          'lorem',
        'Extraction sample ID': 'lorem',
        'Group':                'lorem',
        'Project':              'lorem',
        'Serial no.':           'lorem',
        'concentration after AMPure (ng DNA/\xb5l)': 'lorem',
        'i5':                   'lorem',
        'i5 (Fwd.)':             'lorem',
        'i7':                   'lorem',
        'i7 (Rev.)':            'lorem',
        'total (in 35 µl)':     'lorem',
        'µl for 25 ng':         'lorem'}

# Iterate #
for sample_num, row in df.iterrows():
    data = dict((corr[i], row[i]) for i in row.index)
    data['i5'] = data['i5'][1:]
    data['i7'] = data['i7'][1:]
    text = template % data
    path = "/home/lucass/repos/illumitag/json/presamples/run10/run10-sample%03d.json" % sample_num
    with open(path, 'w') as handle: handle.write(text)
    break