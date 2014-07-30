# Built-in modules #

# Internal modules #
from illumitag.clustering.composition import Composition
from illumitag.common.cache import property_cached
from illumitag.clustering.composition.plots import TaxaBarstack

# Third party modules #

###############################################################################
class CompositionTips(Composition):
    """This taxa are composed of the lowest level"""

    @property_cached
    def taxa_table(self):
        # Return result #
        return self.frame

    @property_cached
    def graphs(self):
        return [TaxaBarstackTips(self)]

    def count_otus(self, speices):
        """How many OTUs got this classification"""
        return len([1 for s in self.taxonomy.assignments.values() if s[-1] == speices])

################################################################################
class TaxaBarstackTips(TaxaBarstack):
    bottom = 0.5
