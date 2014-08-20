# Futures #
from __future__ import division

# Built-in modules #
import os, json

# Internal modules #
from samples import Samples
from outcomes import NoBarcode, OneBarcode, SameBarcode, BadBarcode, GoodBarcode
from quality import QualityReads
from illumitag.groups.fractions import Fractions
from illumitag.helper.primers import TwoPrimers
from fasta import FASTQ
from fasta import PairedFASTQ
from illumitag.running.pool_runner import PoolRunner
from illumitag.graphs import pool_plots
from plumbing.autopaths import AutoPaths
from plumbing.cache import property_cached

# Third party modules #
from tqdm import tqdm

# Constants #
home = os.environ['HOME'] + '/'

###############################################################################
class Pool(object):
    """An illumina MID is called here a 'pool'."""

    all_paths = """
    /samples/
    /groups/
    /graphs/
    /fastqc/
    /logs/
    /quality_reads/
    /quality_reads/fractions/
    /info.json
    """

    kind = 'pool'

    def __repr__(self): return '<%s object "%s">' % (self.__class__.__name__, self.id_name)
    def __str__(self): return self.id_name
    def __iter__(self): return iter(self.children)
    def __len__(self): return self.count
    def __getitem__(self, key): return self.samples[key]

    @property
    def seq_len(self): return len(self.fwd.first_read)

    def __init__(self, json_path, out_dir):
        # Attributes #
        self.out_dir = out_dir
        self.json_path = json_path
        # Parse #
        with open(json_path) as handle: self.info = json.load(handle)
        # Basic #
        self.account = self.info['uppmax_id']
        self.run_num = self.info['run_num']
        self.run_label = self.info['run_id']
        self.project_short_name = self.info['project']
        self.project_long_name = self.info['project_name']
        self.fwd_name = self.info['forward_reads']
        self.rev_name = self.info['reverse_reads']
        # Own attributes #
        self.num = self.info['pool_num']
        self.label = self.info['pool_id']
        self.short_name = self.info['pool']
        self.long_name = self.info['pool_name']
        self.id_name = "run%03d-pool%02d" % (self.run_num, self.num)
        # Special #
        self.samples = Samples(self)
        self.primers = TwoPrimers(self)
        # Second init #
        self.loaded = False

    def load(self):
        """A second __init__ that is delayed, solves some circular references"""
        # Raw file pairs #
        self.fwd_path = home + "/proj/%s/INBOX/%s/%s/%s" % (self.account, self.run_label, self.label, self.fwd_name)
        self.rev_path = home + "/proj/%s/INBOX/%s/%s/%s" % (self.account, self.run_label, self.label, self.rev_name)
        self.fwd = FASTQ(self.fwd_path)
        self.rev = FASTQ(self.rev_path)
        self.fastq = PairedFASTQ(self.fwd.path, self.rev.path, self)
        # Check we can load it #
        if not os.access('/proj/%s' % self.account, os.R_OK):
            raise Exception("You don't have access to the project %s" % self.account)
        if not self.fwd.exists: raise Exception("No file at '%s'" % self.fwd)
        if not self.rev.exists: raise Exception("No file at '%s'" % self.rev)
        # Automatic paths #
        self.base_dir = self.out_dir + self.id_name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)
        # Make an alias to the json #
        self.p.info_json.link_from(self.json_path, safe=True)
        # Children #
        self.samples.load()
        # Check there are 50 #
        assert len(self.samples.children) == 50
        # Barcode length #
        self.bar_len = self.samples.bar_len
        # Make Outcomes #
        self.no_barcodes   = NoBarcode(self)
        self.one_barcodes  = OneBarcode(self)
        self.same_barcodes = SameBarcode(self)
        self.bad_barcodes  = BadBarcode(self)
        self.good_barcodes = GoodBarcode(self)
        self.outcomes = (self.good_barcodes, self.no_barcodes, self.one_barcodes, self.same_barcodes, self.bad_barcodes)
        self.children = self.outcomes
        # The good reads #
        self.quality_reads = QualityReads(self.good_barcodes.assembled.good_primers.len_filtered, self)
        self.fractions = Fractions(self)
        # Runner #
        self.runner = PoolRunner(self)
        # Graphs #
        self.graphs = [getattr(pool_plots, cls_name)(self) for cls_name in pool_plots.__all__]
        # Loaded #
        self.loaded = True
        # Return self for convenience #
        return self

    @property
    def first(self): return self.children[0]

    @property
    def count(self):
        if not self.loaded: self.load()
        return self.fastq.count

    @property
    def avg_quality(self):
        if not self.loaded: self.load()
        return self.fastq.avg_quality

    def __call__(self, *args, **kwargs):
        if not self.loaded: self.load()
        self.runner.run(*args, **kwargs)

    def run_slurm(self, *args, **kwargs):
        if not self.loaded: self.load()
        return self.runner.run_slurm(*args, **kwargs)

    def pool_fastqc(self):
        """Run fastqc on the all the sequences of the pool"""
        if not self.loaded: self.load()
        self.fastq.fastqc(self.p.fastqc_dir)

    def create_outcomes(self):
        """Sort the sequences depending on their barcode status"""
        if not self.loaded: self.load()
        for o in self.outcomes: o.create()
        for r in self.fastq.parse_barcodes():
            if len(r.matches) == 0:                              self.no_barcodes.add_pair(r)
            elif len(r.matches) == 1:                            self.one_barcodes.add_pair(r)
            elif r.matches[0].set == r.matches[1].set:           self.same_barcodes.add_pair(r)
            elif r.matches[0].sample is not r.matches[1].sample: self.bad_barcodes.add_pair(r)
            else:                                                self.good_barcodes.add_pair(r)
        for o in self.outcomes: o.close()

    def create_samples(self):
        """Sort the sequences in different files according to their barcode number
        (if they have one)"""
        if not self.loaded: self.load()
        for sample in self.samples: sample.create()
        for r in tqdm(self.quality_reads.untrimmed.parse_barcodes()): r.first.sample.add_read(r.read)
        for sample in self.samples: sample.close()

    def create_raw_samples(self):
        """Sort the sequences in different files according to their barcode
        before any other quality filtering such as read joining."""
        if not self.loaded: self.load()
        for sample in self.samples: sample.raw.create()
        for r in tqdm(self.good_barcodes.parse_barcodes()): r.first.sample.raw.add_pair(r)
        for sample in self.samples: sample.raw.close()

    def check_fastq_version(self):
        """Let's make sure we are dealing with the Sanger encoding"""
        pass

    def make_pool_plots(self):
        """Call graphs that are in pool_plots.py"""
        if not self.loaded: self.load()
        for graph in self.graphs: graph.plot()

    @property_cached
    def loss_statistics(self):
        """This should be moved to the reporting file"""
        class MessageStat(object):
            def __init__(self, msg, value):
                self.msg = msg
                self.value = value
        class LossStatistics(object):
            def __init__(self, pool): self.pool = pool
            def __iter__(self): return iter((self.outcome, self.assembly, self.primers, self.n_filter, self.qual_filter, self.len_filter))
            @property
            def outcome(self):     return MessageStat("Good barcodes are only %f%% of total",
            (100*len(self.pool.good_barcodes)/self.pool.count))
            @property
            def assembly(self):    return MessageStat("Assembled is only %f%% of good barcodes",
            (100*len(self.pool.good_barcodes.assembled)/len(self.pool.good_barcodes)))
            @property
            def primers(self):    return MessageStat("Good primers is only %f%% of assembled",
            (100*len(self.pool.good_barcodes.assembled.good_primers)/len(self.pool.good_barcodes.assembled)))
            @property
            def n_filter(self):    return MessageStat("N filtered is only %f%% of good primers",
            (100*len(self.pool.good_barcodes.assembled.good_primers.n_filtered)/len(self.pool.good_barcodes.assembled.good_primers)))
            @property
            def qual_filter(self): return MessageStat("Qual filtered is only %f%% of N filtered",
            (100*len(self.pool.good_barcodes.assembled.good_primers.qual_filtered)/len(self.pool.good_barcodes.assembled.good_primers.n_filtered)))
            @property
            def len_filter(self):  return MessageStat("Length filter is only %f%% of qual filtered",
            (100*len(self.pool.good_barcodes.assembled.good_primers.len_filtered)/len(self.pool.good_barcodes.assembled.good_primers.qual_filtered)))
        return LossStatistics(self)

    @property
    def json(self):
        """Regenerate the JSON string for every sample"""
        return ',\n\n'.join(s.json for s in self.samples)
