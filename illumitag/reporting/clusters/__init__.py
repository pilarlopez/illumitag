# Futures #
from __future__ import division

# Built-in modules #
from collections import OrderedDict

# Internal modules #
import illumitag
from illumitag.common import split_thousands, pretty_now
from illumitag.common.autopaths import AutoPaths
from illumitag.reporting.common import HeaderTemplate, FooterTemplate
from illumitag.reporting.common import ScaledFigure #DualFigure,

# Third party modules #
import pystache, sh
from tabulate import tabulate

###############################################################################
class ClusterReport(object):
    """A full report generated in PDF for every Cluster object."""

    all_paths = """
    /report.pdf
    /report.aux
    /report.log
    /report.md
    /report.tex
    /header.tex
    /footer.tex
    """

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, cluster):
        # Attributes #
        self.cluster, self.parent = cluster, cluster
        # Automatic paths #
        self.base_dir = self.cluster.p.report_dir
        self.p = AutoPaths(self.base_dir, self.all_paths)

    def generate(self):
        # Dynamic templates #
        self.md_template = ClusterTemplate(self)
        self.header_template = HeaderTemplate(self, "Auto-generated report")
        self.footer_template = FooterTemplate()
        # Render all the templates #
        self.p.report_md.write(self.md_template.render(), encoding='utf-8')
        self.p.header.write(self.header_template.render())
        self.p.footer.write(self.footer_template.render())
        # Convert the Markdown to LaTeX #
        sh.pandoc(self.p.report_md, read='markdown', write='latex', output=self.p.report_tex)
        # Add the header and footer to that #
        self.p.report_tex.prepend(self.p.header)
        self.p.report_tex.append(self.p.footer)
        # Call XeLaTeX (twice for cross-referencing) #
        self.p.report_aux.remove()
        self.p.report_log.remove()
        self.p.report_pdf.remove()
        sh.xelatex("--interaction=nonstopmode", '-output-directory', self.base_dir, self.p.report_tex, )
        sh.xelatex("--interaction=nonstopmode", '-output-directory', self.base_dir, self.p.report_tex)

###############################################################################
class ClusterTemplate(object):
    """All the parameters to be rendered in the markdown template"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report):
        # Attributes #
        self.report, self.parent = report, report
        self.cluster = self.parent.cluster
        self.project = self.cluster.project

    def render(self, escape=None, delimiters=None):
        if escape is None: escape = lambda u: u
        if delimiters is None: delimiters = (u'{{', u'}}')
        pystache.defaults.DELIMITERS = delimiters
        return pystache.Renderer(escape=escape).render(self)

    # General information #
    def cluster_name(self): return self.cluster.name
    def count_samples(self): return len(self.cluster)
    def project_sentance(self):
        if self.cluster.project is None: return ""
        msg = "It corresponds to project code '%s' ('%s')"
        return msg % (self.cluster.project.name, self.cluster.project.long_name)

    # Samples #
    def sample_table(self):
        # The columns #
        info = OrderedDict((
            ('Name', lambda s: "**" + s.short_name + "**"),
            ('Reference', lambda s: "`" + s.name + "`"),
            ('Description', lambda s: s.long_name),
            ('Reads lost', lambda s: "%.1f%%" % (100-((len(s.fasta)/len(s))*100))),
            ('Reads left', lambda s: split_thousands(len(s.fasta))),
        ))
        # The table #
        rows = [i+1 for i in range(len(self.cluster))]
        columns = info.keys()
        table = [[r] + [info[c](self.cluster[r-1]) for c in columns] for r in rows]
        # Make it as text #
        table = tabulate(table, headers=columns, numalign="right", tablefmt="pipe")
        # Add caption #
        return table + "\n\n   : Summary information for all samples."

    # Processing #
    def illumitag_version(self): return illumitag.__version__
    def git_hash(self): return illumitag.git_repo.hash
    def git_tag(self): return illumitag.git_repo.tag
    def now(self): return pretty_now()
    def results_directory(self): return self.cluster.base_dir

    # Input data #
    def count_sequences(self): return split_thousands(len(self.cluster.reads))
    def input_length_dist(self):
        caption = "Distribution of sequence lengths at input"
        path = self.cluster.reads.graphs[1].path
        label = "input_length_dist"
        return str(ScaledFigure(path, caption, label))

    # Clustering #
    def clustering_citation(self):
        msg = "the %s method (%s). The publication is available at %s"
        return msg % (self.cluster.otus.title, self.cluster.otus.version, self.cluster.otus.article)
    def clustering_graph(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "clustering_graph"
        return str(ScaledFigure(path, caption, label))

    # Classification #
    def classification_citation(self): return split_thousands(len(self.cluster.reads))
    def otus_total(self): return split_thousands(len(self.cluster.reads))
    def otus_classified(self): return split_thousands(len(self.cluster.reads))
    def unwanted_phyla(self): return split_thousands(len(self.cluster.reads))
    def otus_filtered(self): return split_thousands(len(self.cluster.reads))

    # OTU table #
    def otu_sums_graph(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "otu_sums_graph"
        return str(ScaledFigure(path, caption, label))
    def sample_sums_graph(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "sample_sums_graph"
        return str(ScaledFigure(path, caption, label))
    def cumulative_presence(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "cumulative_presence"
        return str(ScaledFigure(path, caption, label))

    # Composition #
    def phyla_composition(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "phyla_composition"
        return str(ScaledFigure(path, caption, label))

    # Composition #
    def standard_nmds(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "standard_nmds"
        return str(ScaledFigure(path, caption, label))
