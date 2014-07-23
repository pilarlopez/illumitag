# Futures #
from __future__ import division

# Built-in modules #
import os, getpass, re

# Internal modules #
import illumitag
from illumitag.common.autopaths import AutoPaths, FilePath

# Third party modules #
import pystache, sh

###############################################################################
class SampleReport(object):
    """A full report generated to PDF for every PreSample object."""

    all_paths = """
    /report.pdf
    /report.aux
    /report.log
    /report.md
    /report.tex
    /header.tex
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
        self.reST_template = RestTemplate(self)
        self.header_template = HeaderTemplate(self)
        # Static templates #
        self.footer_path = FilePath(illumitag.module_dir + "reporting/samples/footer_template.mustache")
        # Render the reStructuredText template #
        pystache.defaults.DELIMITERS = (u'{{', u'}}')
        self.rest_renderer = pystache.Renderer(escape=lambda u: u)
        self.rest_content = self.rest_renderer.render(self.reST_template)
        self.p.report_md.write(self.rest_content,  encoding='utf-8')
        # Convert it to LaTeX #
        sh.pandoc(self.p.report_md, read='markdown', write='latex', output=self.p.report_tex)
        # Render the LaTeX header template #
        pystache.defaults.DELIMITERS = (u'@@[', u']@@')
        self.header_renderer = pystache.Renderer(escape=lambda u: u)
        self.header_content = self.header_renderer.render(self.header_template)
        self.p.header.write(self.header_content)
        # Add the header and footer #
        self.p.report_tex.prepend(self.p.header)
        self.p.report_tex.append(self.footer_path)
        # Call XeLaTeX (twice for cross-referencing) #
        self.p.report_aux.remove()
        self.p.report_log.remove()
        self.p.report_pdf.remove()
        self.out_one = sh.xelatex('-output-directory', self.base_dir, self.p.report_tex)
        self.out_two = sh.xelatex('-output-directory', self.base_dir, self.p.report_tex)

###############################################################################
class RestTemplate(object):
    """All the parameters to be rendered in the reST template"""

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
    def json_path(self):
        url = "https://github.com/limno/illumitag/tree/master/json/presamples"
        url += "/run%03d/run%03d-sample%03d.json"
        return url % (self.presample.run_num, self.presample.run_num, self.presample.num)
    def json_content(self):
        content = self.presample.json_path.read('utf-8')
        content = re.sub('\A(.+?)^    },$', '', content, flags=re.M|re.DOTALL)
        return content.strip('\n }')

    # Processing #
    def illumitag_version(self): return illumitag.__version__
    def git_tag(self): return illumitag.git_tag
    def now(self): return illumitag.git_tag

    # Raw data #
    def fwd_size(self): return str(self.presample.fwd.size)
    def fwd_count(self): return self.presample.fwd.count
    def rev_size(self): return str(self.presample.rev.size)
    def rev_count(self): return self.presample.rev.count

    # Lorem #
    def image_path(self): return self.presample.p.graphs_dir + 'graph.pdf'

###############################################################################
class HeaderTemplate(object):
    """All the parameters to be rendered in the LaTeX header template"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report):
        # Attributes #
        self.report, self.parent = report, report
        self.presample = self.parent.presample

    def name(self):
        if 'USER_FULL_NAME' in os.environ: return os.environ['USER_FULL_NAME']
        else: return "Uppmax user ``%s''" % getpass.getuser()

    def status(self): return os.environ.get('USER_STATUS') or ""
    def company(self): return os.environ.get('USER_COMPANY') or ""
    def subcompany(self): return os.environ.get('USER_SUBCOMPANY') or ""
    def title(self): return "Auto-generated report"

    def image_left(self): return illumitag.module_dir + "reporting/samples/ebc.png"
    def image_right(self): return illumitag.module_dir + "reporting/samples/uu.png"
