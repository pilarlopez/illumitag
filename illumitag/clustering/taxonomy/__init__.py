# Futures #
from __future__ import division

# Built-in modules #
from collections import Counter

# Internal modules #
import illumitag
from illumitag.common import prepend_to_file
from illumitag.common.cache import property_cached
from illumitag.common.autopaths import AutoPaths
from illumitag.fasta.single import FASTA

# Third party modules #
import pandas, numpy

###############################################################################
class Taxonomy(object):
    """Can assign taxonomy to a FASTA file of 16S sequences."""
    unwanted = ['Plastid', 'Mitochondrion', 'Thaumarchaeota', 'Crenarchaeota', 'Euryarchaeota']

    def __repr__(self): return '<%s object of %s>' % (self.__class__.__name__, self.parent)

    def at_level(self, level):
        return dict((k,v[level]) for k,v in self.assignments.items() if len(v) > level)

    def make_plots(self):
        for graph in self.graphs: graph.plot()

    def make_otu_table(self):
        """Asks the counts form the OTU class and does some modifications."""
        # Remove unwanted #
        result = self.otu.cluster_counts_table.copy()
        for otu_name in result:
            species = self.assignments[otu_name]
            if len(species) > 2 and species[2] in self.unwanted: result = result.drop(otu_name, 1)
        # Merge samples when reruns #
        for name, data in result.iterrows():
            sample = [s for s in self.samples if s.short_name == name][0]
            rerun_row = result.loc[name]
            if not sample.info.get('rerun'): continue
            rn, p, n = sample.info['rerun']['run'], sample.info['rerun']['pool'], sample.info['rerun']['num']
            orig_sample = illumitag.runs[rn][p-1][n-1]
            orig_name = orig_sample.short_name
            orig_row = result.loc[orig_name]
            result.loc[orig_name] = orig_row + rerun_row
            result = result.drop(name)
        # Convert to CSV #
        result.to_csv(self.otu_csv, sep='\t')
        prepend_to_file(self.otu_csv, 'X')

    @property_cached
    def otu_table(self):
        return pandas.io.parsers.read_csv(self.otu_csv, sep='\t', index_col=0, encoding='utf-8')

    @property
    def otu_table_norm(self):
        """The same thing as otu_table but normalized so that the sum of a sample is always one"""
        return self.otu_table.apply(lambda x: x/x.sum(), axis=1).replace(numpy.inf, 0.0)

    def make_otu_table_norm(self):
        # Convert to CSV #
        self.otu_table_norm.to_csv(self.otu_csv_norm, sep='\t', float_format='%.40g')
        prepend_to_file(self.otu_csv_norm, 'X')

    def make_filtered_centers(self):
        """Regenerate the centers file with only the OTUs that haven't been
        filtered out previously."""
        self.otus_to_keep = [otu for otu in self.otu_table]
        def filter_otus(f):
            for seq in f:
                if seq.id in self.otus_to_keep: yield seq
        self.centers.write(filter_otus(self.otu.centers))

    def resample_otu_table(self, down_to=5000):
        """This code does not work yet"""
        # Eliminate samples that are under down_to #
        are_high = self.otu_table.sum(axis=1) > down_to
        old_frame = self.otu_table.loc[are_high,:]
        # Determine down_to #
        sums = otus.sum(axis=1)
        if not down_to: self.down_to = min(sums)
        else:
            self.down_to = down_to
            otus = otus.drop(sums[sums < self.down_to].keys())
        # Empty frame #
        subotus = pandas.DataFrame(columns=otus.columns, index=otus.index, dtype=int)
        # Do it #
        for sample_name in otus.index:
            row = otus.loc[sample_name]
            weighted_choices = list(row[row != 0].iteritems())
            population = [val for val, count in weighted_choices for i in range(count)]
            sub_pop = random.sample(population, self.down_to)
            frequencies = Counter(sub_pop)
            new_row = pandas.Series(frequencies.values(), index=frequencies.keys(), dtype=int)
            subotus.loc[sample_name] = new_row

###############################################################################
class SimpleTaxonomy(object):

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.fasta)

    def __init__(self, fasta, base_dir):
        # Base params #
        self.fasta = fasta if isinstance(fasta, FASTA) else FASTA(fasta)
        self.base_dir = base_dir
        self.p = AutoPaths(self.base_dir, self.all_paths)
        # Extra simple composition #
        from illumitag.clustering.composition import SimpleComposition
        self.composition = SimpleComposition(self, self.base_dir + 'comp_' + self.short_name + '/')

    @property_cached
    def phyla(self):
        return Counter(taxa[2] if len(taxa) > 2 else taxa[-1] for taxa in self.assignments.values())