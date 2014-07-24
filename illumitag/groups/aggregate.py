# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from illumitag.common.autopaths import AutoPaths
from illumitag.graphs import aggregate_plots
from illumitag.clustering import Cluster
from illumitag.reporting import Reporter
from illumitag.common.cache import property_cached

# Third party modules #

###############################################################################
class Collection(object):
    """A collection of aggregates."""

    def __repr__(self): return 'Collection: %s' % (self.children)
    def __iter__(self): return iter(self.children)
    def __len__(self): return len(self.children)
    def __add__(self, other): return self.__class__(self.children + other.children)

    def __init__(self, children):
        self.children = children

    @property
    def first(self): return self.children[0]

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return [c for c in self.children if c.name == key.lower()][0]
        elif isinstance(key, int):
            if hasattr(self.first, 'num'): return [c for c in self.children if c.num == key][0]
            else: return self.children[key]
        else: raise TypeError('key')


###############################################################################
class Aggregate(object):
    """A arbitrary aggregate of several pools."""

    all_paths = """
    /graphs/
    /logs/
    /cluster/
    /results/slurm_report.csv
    """

    def __repr__(self): return '<%s object "%s" with %i pools>' % \
                               (self.__class__.__name__, self.name, len(self))
    def __iter__(self): return iter(self.pools)
    def __len__(self): return len(self.pools)
    def __getitem__(self, key):
        if isinstance(key, basestring): return [c for c in self.children if str(c) == key][0]
        elif isinstance(key, int): return self.children[key]
        elif isinstance(key, slice): return self.children[key]
        else: raise TypeError('key')

    @property
    def first(self): return self.pools[0]

    @property
    def count(self): return sum(map(len, self.outcomes))

    def __init__(self, name, pools, out_dir):
        # Attributes #
        self.name = name
        self.pools = pools
        self.loaded = False
        # Dir #
        self.base_dir = out_dir + self.name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)

    def load(self):
        for p in self.pools:
            if not p.loaded: p.load()
        self.loaded = True
        return self

    @property_cached
    def samples(self):
        if self.pools[0].kind == 'presample':  return self.pools
        if self.pools[0].kind == 'pool':       return [s for p in self.pools for s in p.samples]
        if self.pools[0].kind == 'pyrosample': return self.pools

    @property_cached
    def cluster(self): return Cluster(self.samples, self.name, self.p.cluster_dir)

    @property_cached
    def reporter(self): return Reporter(self)

    @property_cached
    def graphs(self): return [getattr(aggregate_plots, cls_name)(self) for cls_name in aggregate_plots.__all__]

    def run_pools(self, steps=None, **kwargs):
        # Check loaded #
        for p in self.pools:
            if not p.loaded: p.load()
        # Call function #
        for p in self.pools: p()

    def run_pools_slurm(self, steps=None, **kwargs):
        return [p.run_slurm(steps, **kwargs) for p in self.pools]

    def make_plots(self):
        if not self.loaded: self.load()
        for graph in self.graphs: graph.plot()