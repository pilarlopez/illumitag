# Futures #
from __future__ import division

# Built-in modules #
import shutil, os

# Internal modules #
from plumbing.autopaths import AutoPaths
from plumbing.cache import property_cached
from plumbing.csv_tables import TSVTable

# Third party modules #
import seqenv

###############################################################################
class Seqenv(object):
    """Base class for Seqenv results processing."""

    all_paths = """
    /abundances.tsv
    """

    def __init__(self, parent, base_dir=None, N=3000, threshold=3.0):
        # Parent #
        self.otu, self.parent = parent, parent
        self.taxonomy = self.parent.taxonomy
        # Other #
        self.N = N
        self.threshold = threshold
        # Directory #
        if base_dir is None: self.base_dir = self.parent.p.seqenv_dir
        else: self.base_dir = base_dir
        self.p = AutoPaths(self.base_dir, self.all_paths)
        # Files #
        self.abundances = TSVTable(self.p.abundances)

    @property_cached
    def analysis(self):
        return seqenv.Analysis(self.taxonomy.centers,
                               out_dir      = self.base_dir,
                               abundances   = self.abundances,
                               N            = self.N,
                               min_identity = (100 - self.threshold) / 100)

    def run(self, cleanup=True):
        # Clean up #
        if cleanup:
            shutil.rmtree(self.base_dir)
            os.mkdir(self.base_dir)
        # Make the abundances file #
        self.taxonomy.otu_csv_norm.transpose(self.abundances, d='\t')
        # Do it #
        self.analysis.run()
