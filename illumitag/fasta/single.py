# Futures #
from __future__ import division

# Built-in modules #
import os, gzip, re
from collections import Counter, OrderedDict

# Internal modules #
from plumbing import isubsample, GenWithLength, imean
from plumbing.autopaths import FilePath, DirectoryPath
from plumbing.tmpstuff import new_temp_path, new_temp_dir
from illumitag.helper.barcodes import ReadWithBarcodes
from illumitag.helper.primers import ReadWithPrimers, ReadWithPrimersMissmatch
from plumbing.cache import property_cached
from plumbing.color import Color
from illumitag.fasta import single_plots, ReadWithIndices, FastQCResults

# Third party modules #
import sh, shutil, regex
from Bio import SeqIO

################################################################################
class FASTA(FilePath):
    """A single FASTA file somewhere in the filesystem"""
    extension = 'fasta'
    buffer_size = 1000

    def __len__(self): return self.count
    def __iter__(self): return self.parse()
    def __repr__(self): return '<%s object on "%s">' % (self.__class__.__name__, self.path)
    def __nonzero__(self): return os.path.exists(self.path) and os.path.getsize(self.path) != 0

    def __init__(self, path, samples=None, primers=None):
        # Basic #
        self.path = path
        # Extra #
        self.samples = samples
        self.primers = primers
        # Graphs #
        graph_params = (self, self.directory + self.prefix.replace('.', '_') + '_')
        self.graphs = [getattr(single_plots, cls_name)(*graph_params) for cls_name in single_plots.__all__]

    @property
    def first_read(self):
        self.open()
        seq = SeqIO.parse(self.handle, self.extension).next()
        self.close()
        return seq

    @property_cached
    def count(self):
        """Should probably check file size instead of just caching once #TODO"""
        if self.path.endswith('gz'): return int(sh.zgrep('-c', "^>", self.path, _ok_code=[0,1]))
        else: return int(sh.grep('-c', "^>", self.path, _ok_code=[0,1]))

    def open(self):
        if self.path.endswith('gz'): self.handle = gzip.open(self.path, 'r')
        else: self.handle = open(self.path, 'r')

    def close(self):
        if hasattr(self, 'buffer'): self.flush()
        self.handle.close()

    def copy(self, path):
        shutil.copy2(self.path, path)

    def create(self):
        self.buffer = []
        self.buf_count = 0
        self.dir = os.path.dirname(self.path)
        if not os.path.exists(self.dir): os.makedirs(self.dir)
        self.handle = open(self.path, 'w')

    def add_read(self, read):
        self.buffer.append(read)
        self.buf_count += 1
        if self.buf_count % self.buffer_size == 0: self.flush()

    def add_seqrecord(self, seqrecord):
        self.buffer.append(seqrecord)
        self.buf_count += 1
        if self.buf_count % self.buffer_size == 0: self.flush()

    def add_iterator(self, reads):
        for read in reads:
            self.buffer.append(read)
            self.buf_count += 1
            if self.buf_count % self.buffer_size == 0: self.flush()

    def flush(self):
        for read in self.buffer: SeqIO.write(read, self.handle, self.extension)
        self.buffer = []

    def write(self, reads):
        self.dir = os.path.dirname(self.path)
        if not os.path.exists(self.dir): os.makedirs(self.dir)
        with open(self.path, 'w') as self.handle: SeqIO.write(reads, self.handle, self.extension)

    def parse(self):
        self.open()
        return SeqIO.parse(self.handle, self.extension)

    def subsample(self, down_to, new_path=None):
        # Auto path #
        if new_path is None: new_path = self.p.subsample
        # Check size #
        if down_to > len(self):
            message = "Can't subsample %s down to %i. Only down to %i."
            print Color.ylw + message % (self, down_to, len(self)) + Color.end
            self.copy(new_path)
            return
        # Make new file #
        cls = FASTQ if self.extension == 'fastq' else FASTA
        self.subsampled = cls(new_path)
        self.subsampled.create()
        # Do it #
        for seq in isubsample(self, down_to):
            self.subsampled.add_seqrecord(seq)
        # Clean up #
        self.subsampled.close()
        # Did it work #
        assert len(self.subsampled) == down_to

    def rename_with_num(self, prefix, new_path=None, remove_desc=True):
        """Rename every sequence based on a prefix and a number"""
        # Temporary path #
        if new_path is None: numbered = self.__class__(new_temp_path())
        else: numbered = self.__class__(new_path)
        # Generator #
        def numbered_iterator():
            for i,read in enumerate(self):
                read.id = prefix + str(i)
                if remove_desc: read.description = ""
                yield read
        # Do it #
        numbered.write(numbered_iterator())
        numbered.close()
        # Replace it #
        if new_path is None:
            os.remove(self.path)
            shutil.move(numbered, self.path)

    def extract_length(self, lower_bound, upper_bound, new_path=None, cls=None):
        """Extract a certain length fraction and place them in a new file"""
        # Temporary path #
        cls = cls or self.__class__
        fraction = cls(new_temp_path()) if new_path is None else cls(new_path)
        # Generator #
        def fraction_iterator():
            for read in self:
                if lower_bound <= len(read) <= upper_bound:
                    yield read
        # Do it #
        fraction.write(fraction_iterator())
        fraction.close()
        return fraction

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

    @property_cached
    def lengths(self):
        return Counter((len(s) for s in self.parse()))

    def lengths_gen(self):
        for s in self.parse(): yield len(s)

    def shorter_than(self, value):
        return 100 * sum((v for k,v in self.lengths.items() if k < value)) / self.count

#-----------------------------------------------------------------------------#
class FASTQ(FASTA):
    """A single FASTQ file somewhere in the filesystem"""
    extension = 'fastq'

    @property_cached
    def count(self):
        if self.path.endswith('gz'): return int(sh.zgrep('-c', "^+$", self.path, _ok_code=[0,1]))
        return int(sh.grep('-c', "^+$", self.path, _ok_code=[0,1]))

    def to_fasta(self, path):
        with open(path, 'w') as handle:
            for r in self: SeqIO.write(r, handle, 'fasta')
        return FASTA(path)

    def to_qual(self, path):
        with open(path, 'w') as handle:
            for r in self: SeqIO.write(r, handle, 'qual')
        return FilePath(path)

    @property_cached
    def avg_quality(self):
        mean = imean(s for r in self for s in r.letter_annotations["phred_quality"])
        self.close()
        return mean

    def fastqc(self, directory=None):
        # Default case #
        if directory is None:
            sh.fastqc(self.path, '-q')
            os.remove(self.prefix_path + '_fastqc.zip')
            return DirectoryPath(self.prefix.split('.')[0] + '_fastqc/')
        # Case directory #
        if directory is not None:
            if not isinstance(directory, DirectoryPath): directory = DirectoryPath(directory)
            if directory.exists: directory.remove()
            tmp_dir = new_temp_dir()
            sh.fastqc(self.path, '-q', '-o', tmp_dir)
            created_dir = tmp_dir + self.prefix.split('.')[0] + '_fastqc/'
            shutil.move(created_dir, directory)
            tmp_dir.remove()
            return directory

    @property
    def fastqc_results(self): return FastQCResults(self.prefix_path + '_fastqc/')

#-----------------------------------------------------------------------------#
class SizesFASTA(FASTA):
    """A Fasta with cluster weights"""

    @property_cached
    def count(self):
        get_size = lambda x: int(re.findall("size=([0-9]+)", x)[0])
        sizes = (get_size(r.description) for r in self)
        return sum(sizes)