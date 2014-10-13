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

main_free = [s.short_name for s in cluster.samples if s.info['Filter_fraction'] == '0.2' and s.info['Tributary'] == '2']
main_atta = [s.short_name for s in cluster.samples if s.info['Filter_fraction'] == '3.0' and s.info['Tributary'] == '2']
trib_free = [s.short_name for s in cluster.samples if s.info['Filter_fraction'] == '0.2' and s.info['Tributary'] == '1']
trib_atta = [s.short_name for s in cluster.samples if s.info['Filter_fraction'] == '3.0' and s.info['Tributary'] == '1']
print "Danube free living: max %.5g, min %.5g"         % (max(summed[main_free]), min(summed[main_free]))
print "Danube attached: max %.5g, min %.5g"            % (max(summed[main_atta]), min(summed[main_atta]))
print "Tributaries attached: max %.5g, min %.5g"       % (max(summed[trib_free]), min(summed[trib_free]))
print "Tributaries free living: max %.5g, min %.5g"    % (max(summed[trib_atta]), min(summed[trib_atta]))