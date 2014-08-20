"""
Special module to demultiplex the odd hybrid run number 5
"""

# Built-in modules #
import os
from collections import Counter

# Internal modules #
import illumitag
from fasta import FASTQ
from fasta import PairedFASTQ
from plumbing.cache import property_cached

# Third party modules #

# Constants #
home = os.environ['HOME'] + '/'

###############################################################################
class Demultiplexer(object):

    def __repr__(self): return '<%s object with %i pools>' % (self.__class__.__name__, len(self.pools))

    def __init__(self, fwd, rev, pools):
        # Attributes #
        self.pools = pools
        self.samples = pools[0].samples
        self.primers = pools[0].primers
        # Files #
        self.fwd = FASTQ(fwd)
        self.rev = FASTQ(rev)
        # Paired #
        self.pair = PairedFASTQ(fwd, rev, self)

    @property_cached
    def barcodes(self):
        return Counter(read.illumina_mid for read in self.pair.parse_barcodes())

###############################################################################
if __name__ == "__main__":
    # Check the unused reads #
    path = home + "proj35/INBOX/131126_M00485_0087_000000000-A6GWG/Undetermined_indices/Sample_lane1/"
    fwd = "lane1_Undetermined_L001_R1_001.fastq.gz"
    rev = "lane1_Undetermined_L001_R2_001.fastq.gz"
    demulti = Demultiplexer(path+fwd, path+rev, illumitag.runs[5])
    print demulti.barcodes.most_common(15)