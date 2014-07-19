#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to convert some TSV files
to our JSON files.
"""

# Modules #
import pandas, codecs

###############################################################################
template = u"""{
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
    "sample_num":    %(sample_num)s,
    "sample_id":     "%(sample_id)s",
    "forward_reads": "%(fwd_filename)s",
    "reverse_reads": "%(rev_filename)s",

    "project":       "%(project)s",
    "project_name":  "%(project_name)s",
    "sample":        "%(sample)s",
    "sample_name":   "%(sample_name)s",
    "group":         "%(group)s",

    "forward_mid":   "%(forward_mid)s",
    "forward_num":   %(forward_num)s,
    "reverse_mid":   "%(reverse_mid)s",
    "reverse_num":   %(reverse_num)s,
    "barcode_num":   %(barcode_num)s,

    "primers": {
            "name":    "General bacteria primers",
            "sense":   "5' to 3'",
            "forward": {"name": "341F", "sequence": "NNNNCCTACGGGNGGCWGCAG"},
            "reverse": {"name": "805R", "sequence": "GACTACHVGGGTATCTAATCC"}
    }

    "library_strategy":     "AMPLICON",
    "library_source":       "METAGENOMIC",
    "library_selection":    "PCR",
    "library_layout":       "Paired-end",
    "platform":             "ILLUMINA",
    "instrument_model":     "Illumina MiSeq",
    "forward_read_length":  300,
    "reverse_read_length":  300,

    "date":         "0000-00-00",
    "latitude":     ["XX°XX'XX''", "N"],
    "longitude":    ["XX°XX'XX''", "E"],
    "location":     "Country: XXX lake",
    "organism":     "aquatic metagenome",

    "bioproject":   "PRJNAXXXXXX",
    "biosample":    "SAMNXXXXXXXX",

    "dna_after_purification": [%(dna)s, "ng/µl"],
}"""

###############################################################################
# Load data #
df = pandas.io.parsers.read_csv('new_data.tsv', sep='\t', encoding='windows-1252', dtype=str)

# Correspondence #
corr = {
    u'Barcode no.':          'barcode_num',
    u'Extraction sample ID': 'sample',
    u'Group':                'group',
    u'Project':              'project',
    u'Serial no.':           'sample_num',
    u'concentration after AMPure (ng DNA/\xb5l)': 'dna',
    u'i5':                   'forward_num',
    u'i5 (Fwd.)':            'forward_mid',
    u'i7':                   'reverse_num',
    u'i7 (Rev.)':            'reverse_mid',
    }

# Iterate #
for i, row in df.iterrows():
    # Transform #
    data = dict((corr[i], row[i]) for i in row.index if i in corr)
    revcompl = lambda x: ''.join([{'A':'T','C':'G','G':'C','T':'A'}[B] for B in x][::-1])
    data['reverse_mid']  = revcompl(data['reverse_mid'])
    data['forward_num']  = data['forward_num'][1:]
    data['reverse_num']  = data['reverse_num'][1:]
    data['project']      = data['project'].lower()
    data['sample']       = data['sample'].lower()
    data['group']        = data['group'].lower()
    data['project_name'] = data['project']
    data['sample_name']  = data['sample']
    filename = "AE_POOL1_2014_%s_%s-%s_L001_R{}_001.fastq.gz" % (data['barcode_num'], data['reverse_mid'], data['forward_mid'])
    data['fwd_filename'] = filename.format("1")
    data['rev_filename'] = filename.format("2")
    data['sample_id']    = "Sample_AE_POOL1_2014_%s" % data['barcode_num']
    data['dna']          = '%s' % float('%.4g' % float(data['dna']))
    # Write #
    text = template % data
    path = "/home/lucass/repos/illumitag/json/presamples/run010/run010-sample%03d.json" % int(data['sample_num'])
    with codecs.open(path, 'w', encoding='utf-8') as handle: handle.write(text)
    break