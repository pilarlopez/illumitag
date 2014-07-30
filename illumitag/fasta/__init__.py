# Built-in modules #

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
        path = FilePath(self.path + 'Images/per_base_quality.png')
        if not path.exists: raise Exception("Attempted to access '%s' which doesn't exist" % path)
        return path

    @property
    def per_seq_qual(self):
        path = FilePath(self.path + 'Images/per_sequence_quality.png')
        if not path.exists: raise Exception("Attempted to access '%s' which doesn't exist" % path)
        return path

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