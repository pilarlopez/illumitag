# Futures #
from __future__ import division

# Built-in modules #
import shutil
from collections import OrderedDict

# Internal modules #
import illumitag
from plumbing.common import split_thousands, pretty_now, andify
from plumbing.autopaths import AutoPaths
from illumitag.reporting.common import HeaderTemplate, FooterTemplate
from illumitag.reporting.common import ScaledFigure

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

    def web_export(self):
        """Copy the report to the webexport directory where it can be viewed by anyone"""
        destination = "/proj/%s/webexport/ILLUMITAG/clusters/%s.pdf"
        destination = destination % (self.cluster.first.account, self.cluster.name)
        shutil.copy(self.p.pdf, destination)

    @property
    def url(self):
        link = "https://export.uppmax.uu.se/%s/ILLUMITAG/clusters/%s.pdf"
        return link % (self.cluster.first.account, self.cluster.name)

###############################################################################
class ClusterTemplate(object):
    """All the parameters to be rendered in the markdown template"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report):
        # Attributes #
        self.report, self.parent = report, report
        self.cluster = self.parent.cluster
        self.project = self.cluster.project
        # Conveniance #
        self.otus = self.cluster.otus
        self.taxonomy = self.otus.taxonomy

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
        table = [[i+1] + [f(self.cluster[i]) for f in info.values()] for i in range(len(self.cluster))]
        # Make it as text #
        table = tabulate(table, headers=info.keys(), numalign="right", tablefmt="pipe")
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
    def clustering_citation(self): return "the %s method (%s)" % (self.otus.title, self.otus.version)
    def clustering_publication(self): return self.otus.article
    def clustering_threshold(self): return "%.1f%%" % self.otus.threshold
    def otus_total(self): return split_thousands(len(self.otus.centers))

    # Classification #
    def classification_citation(self): return "the %s method (%s)" % (self.taxonomy.title, self.taxonomy.version)
    def classification_publication(self): return self.taxonomy.article
    def otus_classified(self): return split_thousands(self.taxonomy.count_assigned)
    def unwanted_phyla(self): return andify(self.taxonomy.unwanted)
    def otus_filtered(self): return split_thousands(len(self.taxonomy.centers))
    def otu_sizes_graph(self):
        caption = "Distribution of OTU sizes"
        path = self.cluster.otus.taxonomy.graphs[0].path
        label = "otu_sizes_graph"
        return str(ScaledFigure(path, caption, label))

    # OTU table #
    def otu_sums_graph(self):
        caption = "Distribution of OTU presence per OTU"
        path = self.cluster.otus.taxonomy.graphs[2].path
        label = "otu_sums_graph"
        return str(ScaledFigure(path, caption, label))
    def sample_sums_graph(self):
        caption = "Distribution of OTU presence per sample"
        path = self.cluster.otus.taxonomy.graphs[1].path
        label = "sample_sums_graph"
        return str(ScaledFigure(path, caption, label))
    def cumulative_presence(self):
        caption = "Cumulative number of reads by OTU presence"
        path = self.cluster.otus.taxonomy.graphs[4].path
        label = "cumulative_presence"
        return str(ScaledFigure(path, caption, label))

    # Taxa table #
    def count_taxa(self): return len(self.cluster.otus.taxonomy.comp_tips)

    # Composition #
    def phyla_composition(self):
        caption = "Species relative abundances per sample on the phyla and class levels"
        path = self.cluster.otus.taxonomy.comp_phyla.graphs[0].path
        label = "phyla_composition"
        return str(ScaledFigure(path, caption, label))

    # Comparison #
    def otu_nmds(self):
        caption = "NMDS using the OTU table for %i samples" % len(self.cluster)
        path = self.cluster.otus.taxonomy.stats.nmds.graph.path
        label = "otu_nmds"
        return str(ScaledFigure(path, caption, label))
    def taxa_nmds(self):
        caption = "NMDS using the taxa table for %i samples" % len(self.cluster)
        path = self.cluster.otus.taxonomy.comp_tips.stats.nmds.graph.path
        label = "taxa_nmds"
        return str(ScaledFigure(path, caption, label))

    # Diversity #
    pass
