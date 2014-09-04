# Built-in modules #
from collections import Counter, OrderedDict

# Internal modules #
from illumitag.helper.primers import ReadWithPrimers, ReadWithPrimersMissmatch
from fasta import FASTA, FASTQ, PairedFASTQ
from plumbing.common import GenWithLength
from plumbing.cache import property_cached

# Third party modules #
import regex

###############################################################################
class BarcodeMatch(object):
    """Given a 7 nucleotide sequence and a collection of samples,
    will find the match if it exists"""

    def __nonzero__(self): return bool(self.set)
    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, str(self))
    def __str__(self): return str(self.sample) + self.set

    def __init__(self, bar, samples):
        # Attributes #
        self.bar = bar
        # Default values #
        index_F, index_R = -1, -1
        self.set, self.sample = None, None
        # Search #
        try: index_F = samples.bars_F.index(bar)
        except ValueError: pass
        try: index_R = samples.bars_R.index(bar)
        except ValueError: pass
        # Record #
        if index_F is not -1:
            self.set = "F"
            self.sample = samples[index_F]
        if index_R is not -1:
            self.set = "R"
            self.sample = samples[index_R]

###############################################################################
class ReadWithBarcodes(object):
    def __init__(self, read, samples):
        self.read = read
        self.bar_len = samples.bar_len
        self.first = BarcodeMatch(str(read.seq)[0:self.bar_len], samples)
        self.last = BarcodeMatch(str(read.reverse_complement().seq)[0:self.bar_len], samples)
        self.matches = (self.first, self.last)

###############################################################################
class ReadPairWithBarcode(object):
    def __init__(self, fwd, rev, samples):
        self.fwd = fwd
        self.rev = rev
        self.samples = samples

    @property
    def matches(self):
        bar_len = self.samples.bar_len
        fwd_m = BarcodeMatch(str(self.fwd.seq)[0:bar_len], self.samples)
        rev_m = BarcodeMatch(str(self.rev.seq)[0:bar_len], self.samples)
        return [m for m in (fwd_m,rev_m) if m]

    @property
    def first(self):
        return self.matches[0]

    @property
    def illumina_mid(self):
        return self.fwd.description[-16:]

###############################################################################
class BarcodedFASTA(FASTA):
    def __init__(self, path, samples, primers=None):
        self.path = path
        self.samples = samples
        self.primers = primers

    def parse_barcodes(self):
        generator = (ReadWithBarcodes(r, self.samples) for r in self.parse())
        return GenWithLength(generator, len(self))

    def parse_primers(self, mismatches=0):
        if mismatches == 0:
            generator = (ReadWithPrimers(r, self.primers) for r in self.parse())
            return GenWithLength(generator, len(self))
        else:
            fwd_regex = regex.compile("(%s){s<=%i}" % (self.primers.fwd_pattern, mismatches))
            rev_regex = regex.compile("(%s){s<=%i}" % (self.primers.rev_pattern, mismatches))
            generator = (ReadWithPrimersMissmatch(r, self.primers, fwd_regex, rev_regex) for r in self.parse())
            return GenWithLength(generator, len(self))

    def parse_indices(self):
        generator = (ReadWithIndices(r) for r in self.parse())
        return GenWithLength(generator, len(self))

    @property_cached
    def barcode_counter(self):
        return Counter((str(m) for read in self.parse_barcodes() for m in read.matches))

    @property_cached
    def good_barcodes_breakdown(self):
        return OrderedDict([(name, self.barcode_counter[name + 'F']) for name in self.samples.bar_names])

    @property_cached
    def indices_counter(self):
        return Counter((r.fwd_index,r.rev_index) for r in self.parse_indices())

###############################################################################
class BarcodedFASTQ(FASTQ, BarcodedFASTA): pass

###############################################################################
class ReadWithIndices(object):
    def __init__(self, read):
        self.read = read
        indices = read.description[-16:]
        self.fwd_index = indices[8:]
        self.rev_index = indices[:8]

###############################################################################
class ReadPairWithIndices(object):
    def __init__(self, fwd, rev):
        self.fwd = fwd
        self.rev = rev
        self.fwd_indices = ReadWithIndices(fwd)
        self.rev_indices = ReadWithIndices(rev)

###############################################################################
class BarcodedPairedFASTQ(PairedFASTQ):
    def __init__(self, path, samples, primers=None):
        self.path = path
        self.samples = samples
        self.primers = primers

    def parse_barcodes(self):
        generator = (ReadPairWithBarcode(f, r, self.samples) for f,r in self.parse())
        return GenWithLength(generator, len(self))

    def parse_indices(self):
        generator = (ReadPairWithIndices(f,r) for f,r in self.parse())
        return GenWithLength(generator, len(self))
