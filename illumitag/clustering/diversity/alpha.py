"""
Check here for the list of estimators:
http://scikit-bio.org/docs/0.1.4/math.diversity.alpha.html
"""

# Built-in modules #

# Internal modules #
from plumbing.graphs import Graph

# Third party modules #
import skbio
import skbio.math.diversity
import skbio.math.diversity.alpha
from matplotlib import pyplot
from skbio.math.subsample import subsample
from numpy import linspace

###############################################################################
class AlphaDiversity(object):
    """All the alpha diversity to be calculated on an OTU table."""

    def __init__(self, parent):
        self.sample, self.parent = parent, parent
        self.chao1   = Chao1(self, base_dir=self.sample.p.graphs_dir)
        self.ace     = Ace(self, base_dir=self.sample.p.graphs_dir)
        self.shannon = Shannon(self, base_dir=self.sample.p.graphs_dir)
        self.simpson = Simpson(self, base_dir=self.sample.p.graphs_dir)
        self.graphs  = [self.chao1, self.ace, self.shannon, self.simpson]

###############################################################################
class AlphaDiversityGraph(Graph):
    bottom = 0.10
    right = 0.96

    @property
    def x(self): return map(int,linspace(0, sum(self.parent.sample.counts), 600))
    @property
    def y(self): return [self.div_fn(subsample(self.parent.sample.counts, k)) for k in self.x]

    def plot(self):
        fig = pyplot.figure()
        axes = fig.add_subplot(111)
        axes.plot(self.x, self.y, 'ro')
        axes.set_title("Rarefaction curve of the " + self.title + " diversity estimate")
        axes.set_xlabel('Sequences rarefied down to this many')
        axes.set_ylabel(self.title + " diversity estimate")
        axes.yaxis.grid(True)
        axes.set_xlim(0, axes.get_xlim()[1])
        self.save_plot(fig, axes, sep=('x',))
        pyplot.close(fig)

###############################################################################
class Chao1(AlphaDiversityGraph):
    """Will graph the Chao1 rarefaction curve."""
    short_name = 'chao1'
    title = "Chao1 (bias-corrected version)"

    @property
    def div_fn(self): return skbio.math.diversity.alpha.chao1

###############################################################################
class Ace(AlphaDiversityGraph):
    """Will graph the Ace rarefaction curve."""
    short_name = 'ace'
    title = "Ace (Abundance-based Coverage Estimator)"

    @property
    def div_fn(self): return skbio.math.diversity.alpha.ace

    @property
    def x(self):
        total = sum(self.parent.sample.counts)
        return map(int,linspace(total/2, total, 600))

###############################################################################
class Shannon(AlphaDiversityGraph):
    """Will graph the Shannon rarefaction curve."""
    short_name = 'shannon'
    title = "Shannon (entropy of counts H, in bits)"

    @property
    def div_fn(self): return skbio.math.diversity.alpha.shannon

###############################################################################
class Simpson(AlphaDiversityGraph):
    """Will graph the Simpson rarefaction curve."""
    short_name = 'simpson'
    title = "Simpson (1 - dominance)"

    @property
    def div_fn(self): return skbio.math.diversity.alpha.simpson