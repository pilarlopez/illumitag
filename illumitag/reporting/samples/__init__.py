# Futures #
from __future__ import division

# Built-in modules #
import re, datetime

# Internal modules #
import illumitag
from illumitag.common.autopaths import AutoPaths
from illumitag.reporting.common import HeaderTemplate, FooterTemplate
from illumitag.reporting.common import DualFigure

# Third party modules #
import pystache, sh, dateutil

###############################################################################
class SampleReport(object):
    """A full report generated in PDF for every PreSample object."""

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

    def __init__(self, presample):
        # Attributes #
        self.presample, self.parent = presample, presample
        # Automatic paths #
        self.base_dir = self.presample.p.report_dir
        self.p = AutoPaths(self.base_dir, self.all_paths)

    def generate(self):
        # Dynamic templates #
        self.md_template = SampleTemplate(self)
        self.header_template = HeaderTemplate(self, "Auto-generated report")
        self.footer_template = FooterTemplate()
        # Render the LaTeX header template #
        pystache.defaults.DELIMITERS = (u'@@[', u']@@')
        self.header_renderer = pystache.Renderer(escape=lambda u: u)
        self.header_content = self.header_renderer.render(self.header_template)
        self.p.header.write(self.header_content)
        # Render the LaTeX footer template #
        self.footer_renderer = pystache.Renderer(escape=lambda u: u)
        self.footer_content = self.footer_renderer.render(self.footer_template)
        self.p.footer.write(self.footer_content)
        # Render the markdown template #
        pystache.defaults.DELIMITERS = (u'{{', u'}}')
        self.md_renderer = pystache.Renderer(escape=lambda u: u)
        self.md_content = self.md_renderer.render(self.md_template)
        self.p.report_md.write(self.md_content, encoding='utf-8')
        # Convert it to LaTeX #
        sh.pandoc(self.p.report_md, read='markdown', write='latex', output=self.p.report_tex)
        # Add the header and footer #
        self.p.report_tex.prepend(self.p.header)
        self.p.report_tex.append(self.p.footer)
        # Call XeLaTeX (twice for cross-referencing) #
        self.p.report_aux.remove()
        self.p.report_log.remove()
        self.p.report_pdf.remove()
        sh.xelatex("--interaction=nonstopmode", '-output-directory', self.base_dir, self.p.report_tex, )
        sh.xelatex("--interaction=nonstopmode", '-output-directory', self.base_dir, self.p.report_tex)

###############################################################################
class SampleTemplate(object):
    """All the parameters to be rendered in the markdown template"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report):
        # Attributes #
        self.report, self.parent = report, report
        self.presample = self.parent.presample
        self.project = self.presample.project

    # General information #
    def sample_short_name(self): return self.presample.short_name
    def sample_long_name(self): return self.presample.short_name
    def project_short_name(self): return self.presample.project_short_name
    def project_long_name(self): return self.presample.project_long_name
    def project_other_samples(self): return len(self.project) - 1

    # JSON #
    def json_url(self):
        url = "https://github.com/limno/illumitag/tree/master/json/presamples"
        url += "/run%03d/run%03d-sample%03d.json"
        return url % (self.presample.run_num, self.presample.run_num, self.presample.num)
    def json_content(self):
        content = self.presample.json_path.read('utf-8')
        content = re.sub('\A(.+?)^    },$', '', content, flags=re.M|re.DOTALL)
        return content.strip('\n }')

    # Processing #
    def illumitag_version(self): return illumitag.__version__
    def git_hash(self): return illumitag.git_repo.hash
    def git_tag(self): return illumitag.git_repo.tag
    def now(self):
        now = datetime.datetime.now(dateutil.tz.tzlocal())
        return now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    def results_directory(self): return self.presample.base_dir

    # Raw data #
    def fwd_size(self): return str(self.presample.fwd.size)
    def fwd_count(self): return self.presample.fwd.count
    def fwd_qual(self): return "%.2f" % self.presample.fwd.avg_quality
    def rev_size(self): return str(self.presample.rev.size)
    def rev_count(self): return self.presample.rev.count
    def rev_qual(self): return "%.2f" % self.presample.rev.avg_quality
    def illumina_report(self): return self.presample.run.html_report_path
    def per_base_qual(self):
        params = [self.presample.fwd_fastqc.per_base_qual, self.presample.rev_fastqc.per_base_qual]
        params += ["Forward", "Reverse"]
        params += ["fwd_per_base_qual", "rev_fwd_per_base_qual"]
        params += ["Per base quality", "per_base_qual"]
        return str(DualFigure(*params))
    def per_seq_qual(self):
        params = [self.presample.fwd_fastqc.per_seq_qual, self.presample.rev_fastqc.per_seq_qual]
        params += ["Forward", "Reverse"]
        params += ["fwd_per_seq_qual", "rev_fwd_per_seq_qual"]
        params += ["Per sequence quality", "per_seq_qual"]
        return str(DualFigure(*params))

    # Lorem #
    def image_path(self): return self.presample.p.graphs_dir + 'graph.pdf'