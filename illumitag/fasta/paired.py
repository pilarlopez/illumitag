# Built-in modules #
import os, sys, gzip
from itertools import izip

# Internal modules #
from illumitag.common import GenWithLength
from illumitag.helper.barcodes import ReadPairWithBarcode
from illumitag.common.cache import property_cached
from illumitag.fasta.single import FASTQ
from illumitag.common.autopaths import DirectoryPath

# Third party modules #
import sh
from Bio import SeqIO

###############################################################################
class PairedFASTQ(object):
    """Read and write FASTQ file pairs without using too much RAM"""
    buffer_size = 1000

    def __len__(self): return self.count
    def __iter__(self): return self.parse()
    def __repr__(self): return '<%s object on "%s">' % (self.__class__.__name__, self.fwd_path)

    def __init__(self, fwd_path, rev_path, parent):
        # Basic #
        self.fwd_path = fwd_path
        self.rev_path = rev_path
        # File objects #
        self.fwd = FASTQ(fwd_path)
        self.rev = FASTQ(rev_path)
        # Extra #
        self.pool, self.parent = parent, parent
        self.samples = parent.samples
        self.primers = parent.primers
        self.gziped = True if self.fwd_path.endswith('gz') else False

    @property_cached
    def count(self):
        if self.gziped: return int(sh.zgrep('-c', "^+$", self.fwd_path, _ok_code=[0,1]))
        else: return int(sh.grep('-c', "^+$", self.fwd_path, _ok_code=[0,1]))

    @property
    def exists(self): return self.fwd.exists and self.rev.exists

    @property
    def avg_quality(self): return (self.fwd.avg_quality, self.rev.avg_quality)

    def open(self):
        # Fwd #
        if self.gziped: self.fwd_handle = gzip.open(self.fwd_path, 'r')
        else:           self.fwd_handle = open(self.fwd_path, 'r')
        # Rev #
        if self.gziped: self.rev_handle = gzip.open(self.rev_path, 'r')
        else:           self.rev_handle = open(self.rev_path, 'r')

    def close(self):
        if hasattr(self, 'buffer'): self.flush()
        self.fwd_handle.close()
        self.rev_handle.close()

    def create(self):
        # The buffer #
        self.buffer = []
        self.buf_count = 0
        # Directory #
        self.fwd_dir = os.path.dirname(self.fwd_path)
        self.rev_dir = os.path.dirname(self.rev_path)
        if not os.path.exists(self.fwd_dir): os.makedirs(self.fwd_dir)
        if not os.path.exists(self.rev_dir): os.makedirs(self.rev_dir)
        # The files #
        self.fwd_handle = open(self.fwd_path, 'w')
        self.rev_handle = open(self.rev_path, 'w')

    def add_pair(self, pair):
        self.buffer.append(pair)
        self.buf_count += 1
        if self.buf_count % self.buffer_size == 0:
            sys.stderr.write('.')
            self.flush()

    def flush(self):
        for pair in self.buffer:
            SeqIO.write(pair.fwd, self.fwd_handle, 'fastq')
            SeqIO.write(pair.rev, self.rev_handle, 'fastq')
        self.buffer = []

    def fastqc(self, directory):
        """Run FASTQC on both files and put results in a directory"""
        if not isinstance(directory, DirectoryPath): directory = DirectoryPath(directory)
        if not directory.exists: directory.create()
        self.fwd.fastqc(directory + 'fwd_fastqc/')
        self.rev.fastqc(directory + 'rev_fastqc/')

    def parse(self):
        self.open()
        return izip(SeqIO.parse(self.fwd_handle, 'fastq'),
                    SeqIO.parse(self.rev_handle, 'fastq'))

    def parse_barcodes(self):
        generator = (ReadPairWithBarcode(f, r, self.samples) for f,r in self.parse())
        return GenWithLength(generator, len(self))