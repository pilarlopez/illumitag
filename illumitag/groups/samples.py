# Built-in modules #
import json, re
from collections import OrderedDict
from ftputil import FTPHost

# Internal modules #
from illumitag.fasta.single import FASTQ, FASTA
from illumitag.fasta.paired import PairedFASTQ
from illumitag.common.autopaths import AutoPaths
from illumitag.common import Password

# Third party modules #

# Constants #
ftp_server = "webin.ebi.ac.uk"
ftp_login = "Webin-38108"
ftp_password = Password("ENA FTP password for user '%s':" % ftp_login)

###############################################################################
class Samples(object):
    """A list-like container for all samples of a pool"""

    def __repr__(self): return '<%s object for pool %s>' % (self.__class__.__name__, self.parent)
    def __iter__(self): return iter(self.children)
    def __len__(self): return len(self.children)
    def __getitem__(self, key): return self.children[key]

    @property
    def first(self): return self.children[0]

    def __init__(self, parent):
        # Basic #
        self.parent, self.pool = parent, parent
        self.info = parent.info['samples']
        self.children = [Sample(s, self) for s in self.info]
        # Sort them #
        self.children.sort(key=lambda x: x.num)
        # Check names are unique #
        names = [s.short_name for s in self if s.used]
        assert len(names) == len(set(names))

    def load(self):
        # Barcodes #
        self.bars_F = [s.fwd_str for s in self]
        self.bars_R = [s.rev_str for s in self]
        # Barcode names #
        self.bar_names = ['barcode%i' % s.num for s in self]
        self.bar_sided_names = [name + side for name in self.bar_names for side in ('F','R')]
        self.bar_names_F = [name + 'F' for name in self.bar_names]
        self.bar_names_R = [name + 'R' for name in self.bar_names]
        self.all_bar_pairs = [(a,b) for a in self.bar_sided_names for b in self.bar_sided_names if a[:-1] != b[:-1]]
        # Barcode length #
        self.bar_len = len(self.first.fwd_str)
        # Primer size #
        self.trim_fwd = self.bar_len + self.pool.primers.fwd_len
        self.trim_rev = self.bar_len + self.pool.primers.rev_len
        # Children #
        for s in self: s.load()

###############################################################################
class Sample(FASTQ):
    """All sequences with the same barcode pair grouped together"""

    all_paths = """
    /orig.fastq
    /trimmed.fastq
    /renamed.fastq
    /reads.fasta
    /raw/fwd.fastq
    /raw/rev.fastq
    /raw/forward.fastq.gz
    /raw/reverse.fastq.gz
    """

    def __repr__(self): return '<%s object "%s">' % (self.__class__.__name__, self.name)
    def __str__(self): return self.bar_name

    def __init__(self, info, parent):
        # Save attributes #
        self.info = info
        self.parent = parent
        self.pool = parent.pool
        # Basic #
        self.short_name = info['name']
        self.group_name = info['group']
        self.num = int(info['num'])
        self.used = bool(info['used'])
        self.fwd_str = info['fwd']
        self.rev_str = info['rev']
        # Other #
        self.bar_name = 'barcode%i' % self.num
        self.name = 'run%i_pool%i_sample%i' % (self.pool.run_num, self.pool.num, self.num)

    def load(self):
        # Special case for dummy samples #
        if self.info.get('dummy'): return
        # Paths #
        self.base_dir = self.pool.p.samples_dir + self.bar_name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)
        self.path = str(self.p.orig_fastq)
        # Distances #
        self.trim_fwd = self.pool.samples.trim_fwd
        self.trim_rev = self.pool.samples.trim_rev
        # Files #
        self.trimmed = FASTQ(self.p.trimmed)
        self.renamed = FASTQ(self.p.renamed)
        self.fasta = FASTA(self.p.reads_fasta)
        self.raw = PairedFASTQ(self.p.raw_fwd, self.p.raw_rev, self.pool)
        self.raw_gz = PairedFASTQ(self.p.raw_forward_gz, self.p.raw_reverse_gz, self.pool)

    def process(self):
        def no_primers_iterator(reads):
            for read in reads:
                yield read[self.trim_fwd:-self.trim_rev]
        self.trimmed.write(no_primers_iterator(self))
        self.trimmed.rename_with_num(self.name + '_read', self.renamed)
        self.renamed.to_fasta(self.fasta)

    @property
    def json(self):
        """Regenerate the JSON string from the object including extra info"""
        result = OrderedDict([(k, self.info[k]) for k in ('name', 'used', 'group', 'num', 'fwd', 'rev')])
        result = json.dumps(result)
        if self.extra_metadata:
            result = result[:-1] + ',' + json.dumps(self.extra_metadata, indent=4)[1:]
            result = re.compile(r'\bNaN\b').sub('null', result)
        return result

    @property
    def count_raw_reads(self):
        """The number of reads the sample originally had right after barcode processing and before any other quality filtering"""
        return self.pool.good_barcodes.breakdown[self.bar_name]

    def upload_to_ena(self):
        """Upload the raw reads file (gziped) to the European Nucleotide Archive"""
        # Connect #
        ftp = FTPHost(ftp_server, ftp_login, str(ftp_password))
        # Gzip if not there yet #
        if not self.raw_gz.exists:
            self.raw.fwd.gzip_to(self.p.raw_forward_gz)
            self.raw.rev.gzip_to(self.p.raw_reverse_gz)
        # Make directory #
        directory = '/ILLUMITAG/run%03d/pool%02d/sample%02d/'
        directory = directory % (self.pool.run_num, self.pool.num, self.num)
        ftp.makedirs(directory)
        # Upload #
        base_path = directory + 'run%03d_pool%02d_sample%02d_{}_reads.fastq.gz'
        base_path = base_path % (self.pool.run_num, self.pool.num, self.num)
        ftp.upload(self.p.raw_forward_gz, base_path.format("forward"))
        ftp.upload(self.p.raw_reverse_gz, base_path.format("reverse"))
        # Return #
        ftp.quit()