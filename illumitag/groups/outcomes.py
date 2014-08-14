# Built-in modules #
import os
from collections import Counter, defaultdict, OrderedDict

# Internal modules #
from assemble import Assembled, Unassembled
from illumitag.fasta.paired import PairedFASTQ
from illumitag.graphs import outcome_plots
from illumitag.common.cache import property_cached
from illumitag.common.autopaths import AutoPaths

# Third party modules #
import sh, numpy
from shell_command import shell_call

###############################################################################
class BarcodeGroup(PairedFASTQ):
    """A bunch of sequences all having the same type of barcode outcome"""
    short_name = "generic_barcode_outcome"

    all_paths = """
    /fwd.fastq
    /rev.fastq
    /graphs/
    /assembled/
    /unassembled/
    """

    def __iter__(self): return iter(self.children)
    def __repr__(self): return '<%s object of pool %i>' % (self.__class__.__name__, self.pool.num)

    def __init__(self, parent):
        # Save parent #
        self.parent, self.pool = parent, parent
        self.samples = parent.samples
        # Paths #
        self.base_dir = self.pool.p.groups_dir + self.short_name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)
        # Super #
        self.fwd_path = self.p.fwd_fastq
        self.rev_path = self.p.rev_fastq
        self.gziped = True if self.fwd_path.endswith('gz') else False
        # Add assembly files #
        self.assembled = Assembled(self)
        self.unassembled = Unassembled(self)
        self.children = (self.assembled, self.unassembled)
        self.first = self.assembled
        # Graphs #
        self.graphs = [getattr(outcome_plots, cls_name)(self) for cls_name in outcome_plots.__all__]

    def assemble(self):
        """A better term than assemble would be 'join' since there are only pairs
        Uses pandaseq 2.7"""
        self.assembled.remove()
        command = 'pandaseq27 -T 1 -f %s -r %s -u %s -F 1> %s 2> %s'
        command = command % (self.fwd_path, self.rev_path, self.unassembled.path, self.assembled.path, self.assembled.p.out)
        shell_call(command) # Because it exits with status 1 https://github.com/neufeld/pandaseq/issues/40

    def check_noalign_counts(self):
        """Check the sanity of pandaseq"""
        assert len(self.assembled) + len(self.unassembled) + self.assembled.stats['lowqual'] == len(self)
        assert self.assembled.stats['noalign'] == self.unassembled.count

    def barcode_fastqc(self):
        sh.fastqc(self.fwd_path, '-q')
        os.remove(os.path.splitext(self.fwd_path)[0] + '_fastqc.zip')
        sh.fastqc(self.rev_path, '-q')
        os.remove(os.path.splitext(self.rev_path)[0] + '_fastqc.zip')

    def assembly_fastqc(self):
        sh.fastqc(self.assembled.path, '-q')
        os.remove(os.path.splitext(self.assembled.path)[0] + '_fastqc.zip')

    def make_outcome_plots(self):
        for graph in self.graphs: graph.plot()

###############################################################################
class NoBarcode(BarcodeGroup):
    short_name = "no_barcodes"
    doc = "No barcodes found at all"

    @property_cached
    def counter(self):
        return Counter()

#-----------------------------------------------------------------------------#
class OneBarcode(BarcodeGroup):
    short_name = "one_barcodes"
    doc = "Only one barcode found"

    @property_cached
    def counter(self):
        return Counter(str(p.matches[0]) for p in self.parse_barcodes())

#-----------------------------------------------------------------------------#
class SameBarcode(BarcodeGroup):
    """When the barcodes have a set discrepancy"""
    short_name = "same_barcodes"
    doc = "Both barcodes in same set"

    @property_cached
    def set_counter(self):
        return Counter(frozenset(map(str,p.matches)) for p in self.parse_barcodes())

    @property_cached
    def counter(self):
        return Counter(str(m) for pair in self.parse_barcodes() for m in pair.matches)

#-----------------------------------------------------------------------------#
class BadBarcode(BarcodeGroup):
    """When the barcodes have an index discrepancy"""
    short_name = "bad_barcodes"
    long_name = "mismatching barcodes"
    doc = "The two barcodes mismatch"

    @property_cached
    def set_counter(self):
        return Counter(frozenset(map(str,p.matches)) for p in self.parse_barcodes())

    @property_cached
    def counter(self):
        return Counter(str(m) for pair in self.parse_barcodes() for m in pair.matches)

    @property_cached
    def distribution(self):
        result = defaultdict(Counter)
        for k,v in self.set_counter.items():
            first, second = k
            result[first][second] = v
            result[second][first] = v
        return result

#-----------------------------------------------------------------------------#
class GoodBarcode(BarcodeGroup):
    short_name = "good_barcodes"
    long_name = "matching barcodes"
    doc = "Success: barcodes match"

    @property_cached
    def counter(self):
        """Keys are of type 'barcode42F' and 'barcode42R'"""
        return Counter(str(m) for pair in self.parse_barcodes() for m in pair.matches)

    @property_cached
    def breakdown(self):
        return OrderedDict([(name, self.counter[name + 'F']) for name in self.samples.bar_names])

    @property
    def relative_std_dev(self):
        return numpy.std(self.breakdown.values()) / numpy.mean(self.breakdown.values())