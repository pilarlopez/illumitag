# Built-in modules #
import re

# Internal modules #
from illumitag.common.autopaths import FilePath, DirectoryPath

# Third party modules #

###############################################################################
class FastQCResults(DirectoryPath):
    """A directory with the results from FastQC"""

    def __init__(self, directory):
        if not directory.endswith('/'): directory += '/'
        self.path = directory

    @property
    def per_base_qual(self):
        return FilePath(self.path + 'Images/per_base_quality.png')

    @property
    def per_seq_qual(self):
        return FilePath(self.path + 'Images/per_sequence_quality.png')


###############################################################################
class ReadWithIndices(object):
    def __init__(self, read):
        self.read = read
        indices = re.findall('1:N:0:([ATGCN]+)', read.description)[0]
        self.fwd_index = indices[:8]
        self.rev_index = indices[8:]