# Built-in modules #
from collections import Counter, OrderedDict
import locale

# Internal modules #
from illumitag.graphs import Graph, cool_colors
from plumbing import flatten
from illumitag.helper.silvamod import amplified

# Third party modules #
import pandas, matplotlib
from matplotlib import pyplot

# Constants #
__all__ = ['BarcodeStack', 'AssemblyCounts', 'ChimerasSummary', 'LengthDistribution', 'FractionTaxaBarStack']

################################################################################
class BarcodeStack(Graph):
    """General distribution of barcodes for all pools"""
    short_name = 'barcode_stack'
    left = 0.1
    right = 0.96

    def plot(self):
        # Data #
        rows = ["Pool %i" % p.num for p in reversed(self.parent.pools)]
        columns = [o.doc for o in self.parent.first.outcomes]
        data = [[o.count for o in p.outcomes] for p in reversed(self.parent.pools)]
        self.frame = pandas.DataFrame(data, index=rows, columns=columns)
        # Plot #
        fig = pyplot.figure()
        axes = self.frame.plot(kind='barh', stacked=True, color=['g','k','y','orange','r'])
        fig = pyplot.gcf()
        # Other #
        axes.set_title('Demultiplexing result (%i barcodes are used)' % len(self.parent.first.samples))
        axes.set_xlabel('Number of paired reads')
        axes.xaxis.grid(True)
        axes.yaxis.grid(False)
        # Save it #
        self.save_plot(fig, axes, sep=('x'))
        self.frame.to_csv(self.csv_path)
        pyplot.close(fig)

################################################################################
class AssemblyCounts(Graph):
    """Do the reads assemble together or not"""
    short_name = 'assembly_counts'

    def plot(self):
        # Data #
        rows = ['Pool "%s" (%s)' % (p.long_name, p) for p in self.parent.pools]
        columns = flatten([(o.short_name + "_ass", o.short_name + "_unass") for o in self.parent.first.outcomes])
        data = [flatten([(len(o.assembled), len(o.unassembled)) for o in pool.outcomes]) for pool in self.parent.pools]
        self.frame = pandas.DataFrame(data, index=rows, columns=columns)
        # Plot #
        fig = pyplot.figure()
        colors = ['g','g','gray','gray','y','y','orange','orange','r','r']
        axes = self.frame.plot(kind='barh', stacked=True, color=colors)
        fig = pyplot.gcf()
        # Add pattern #
        unass_patches = [p for i,p in enumerate(axes.patches) if (i/len(self.parent))%2 == 1]
        for p in unass_patches: p.set_hatch('//')
        # Other #
        axes.set_title('Assembling reads using PANDAseq')
        axes.set_xlabel('Number of paired reads')
        axes.xaxis.grid(True)
        # Save it #
        self.save_plot(fig, axes, sep=('x'))
        self.frame.to_csv(self.csv_path)
        pyplot.close(fig)

################################################################################
class ChimerasSummary(Graph):
    """Aggregate the chimeras results"""
    short_name = 'chimeras_summary'

    def plot(self):
        # Data #
        rows = []
        for a in ('uchime_ref', 'uchime_denovo'):
            for p in self.parent.pools:
                for t in ('good_barcodes', 'bad_barcodes'):
                    rows.append(getattr(getattr(p, t).assembled.good_primers,a))
        self.frame = pandas.Series(map(lambda x: x.percent,rows), index=map(str,rows))
        # Plot #
        fig = pyplot.figure()
        axes = self.frame.plot(kind='barh')
        fig = pyplot.gcf()
        # Other #
        axes.set_title('Chimeras detection results')
        axes.set_xlabel('Percentage of sequences identified as chimeras after quality filtering')
        axes.xaxis.grid(True)
        # Save it #
        self.save_plot(fig, axes, sep=('x'), left=0.3)
        self.frame.to_csv(self.csv_path)
        pyplot.close(fig)

################################################################################
class LengthDistribution(Graph):
    """Distribution of assembly lengths with added
    distribution from the Silvamod database"""
    short_name = 'length_distribution'

    def plot(self):
        # Data #
        counts = sum((p.quality_reads.only_used.lengths for p in self.parent), Counter())
        # Plot #
        fig = pyplot.figure()
        pyplot.bar(counts.keys(), counts.values(), 1.0, color='gray', align='center',
                   label='Reads from soil sample')
        title = 'Distribution of sequence lengths for quality filtered reads.'
        axes = pyplot.gca()
        axes.set_title(title)
        axes.set_xlabel('Length of sequence in nucleotides')
        axes.set_ylabel('Number of sequences with this length')
        axes.yaxis.grid(True)
        # Add Silvamod lengths on second scale #
        silva_counts = amplified.lengths
        silvas_axes = axes.twinx()
        silvas_axes.plot(silva_counts.keys(), silva_counts.values(), 'r-',
                         label='Sequences from the silvamod database')
        silvas_axes.set_ylabel('Number of sequences from the silvamod database', color='r')
        for tick in silvas_axes.get_yticklabels(): tick.set_color('r')
        # Legends #
        axes.legend(loc='upper left')
        silvas_axes.legend(loc='upper right')
        # Add separator #
        locale.setlocale(locale.LC_ALL, '')
        seperate = lambda x,pos: locale.format("%d", x, grouping=True)
        silvas_axes.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(seperate))
        # Change ticks #
        import matplotlib.ticker as mticker
        myLocator = mticker.MultipleLocator(10)
        axes.xaxis.set_major_locator(myLocator)
        axes.set_xlim(400, 500)
        # Save it #
        self.save_plot(fig, axes, sep=('y'), width=14.0, height=8.0, bottom=0.08, top=0.95, left=0.08, right=0.92)
        # Save CSV #
        self.frame = pandas.Series(counts.get(i,0) for i in range(max(counts.keys())+1))
        self.frame.to_csv(self.csv_path)
        pyplot.close(fig)

################################################################################
class FractionTaxaBarStack(Graph):
    """Comparing all fractions across all pools in a barstack"""
    short_name = 'fraction_taxa_barstack'

    def plot(self):
        self.frame = OrderedDict((('%s - %s' % (p,f), getattr(p.fractions, f).rdp.phyla)
                     for f in ('low', 'med', 'big') for p in self.parent.pools))
        self.frame = pandas.DataFrame(self.frame)
        self.frame = self.frame.fillna(0)
        self.frame = self.frame.transpose()
        self.frame = self.frame.apply(lambda x: 100*x/x.sum(), axis=1)
        # Sort the table by sum #
        sums = self.frame.sum()
        sums.sort(ascending=False)
        self.frame = self.frame.reindex_axis(sums.keys(), axis=1)
        # Plot #
        fig = pyplot.figure()
        axes = self.frame.plot(kind='bar', stacked=True, color=cool_colors)
        fig = pyplot.gcf()
        # Other #
        axes.set_title('Species relative abundances per fraction per pool')
        axes.set_ylabel('Relative abundances in percent')
        axes.xaxis.grid(False)
        axes.yaxis.grid(False)
        axes.set_ylim([0,100])
        # Put a legend below current axis
        axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=5)
        # Save it #
        self.save_plot(fig, axes, width=24.0, height=14.0, bottom=0.30, top=0.97, left=0.04, right=0.98)
        self.frame.to_csv(self.csv_path)
        pyplot.close(fig)
