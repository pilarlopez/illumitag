#!/usr/bin/env python2

"""
A script to get some numbers.
"""

# Future #
from __future__ import division

# Modules #
import illumitag

###############################################################################
cluster = illumitag.clustering.favorites.danube.load()
comp = cluster.otu_uparse.taxonomy_fw.comp_tips
norm = comp.frame.apply(lambda x: x/x.sum(), axis=1) # Every sample sums to one
tribes = ['LD12', 'acI-B1', 'acI-A7', 'acI-C2']
summed = norm[tribes].sum(axis=1)

print "Global: max %.5g, min %.5g" % (max(summed), min(summed))

free_living = [s.short_name for s in cluster.samples if s.info['Filter_fraction'] == '0.2']
attached =    [s.short_name for s in cluster.samples if s.info['Filter_fraction'] == '3.0']
print "Free living: max %.5g, min %.5g" % (max(summed[free_living]), min(summed[free_living]))
print "Attached: max %.5g, min %.5g"    % (max(summed[attached]),    min(summed[attached]))

main_river =  [s.short_name for s in cluster.samples if s.info['Tributary'] == '2']
tributaries = [s.short_name for s in cluster.samples if s.info['Tributary'] == '1']
print "Main river: max %.5g, min %.5g"  % (max(summed[main_river]),  min(summed[main_river]))
print "Tributaries: max %.5g, min %.5g" % (max(summed[tributaries]), min(summed[tributaries]))
