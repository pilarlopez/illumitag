#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
They counted 90 samples instead of 96. We have to demultiplex them
"""

# Modules #
import illumitag

###############################################################################
undetermined = illumitag.runs[10][-1]
#print s.fwd.indices_counter.most_common(100)

missing = {
 "Sample_AE_POOL1_2014_96": ('TCCTCTAC', 'CTAAGCCT'),
 "Sample_AE_POOL1_2014_95": ('TGCCTCTT', 'CTAAGCCT'),
 "Sample_AE_POOL1_2014_94": ('CAGCCTCG', 'CTAAGCCT'),
 "Sample_AE_POOL1_2014_93": ('AGCGTAGC', 'CTAAGCCT'),
 "Sample_AE_POOL1_2014_92": ('CCTCTCTG', 'CTAAGCCT'),
 "Sample_AE_POOL1_2014_91": ('GTAGAGAG', 'CTAAGCCT'),
}

missing = illumitag.runs[10][90:96]
for s in missing: s.fish_out(undetermined)