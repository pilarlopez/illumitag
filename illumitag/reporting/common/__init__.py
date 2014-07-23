# Futures #
from __future__ import division

# Built-in modules #
import os, getpass

# Internal modules #
import illumitag

# Third party modules #
import pystache

###############################################################################
class HeaderTemplate(object):
    """All the parameters to be rendered in the LaTeX header template"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report, title):
        # Attributes #
        self.report, self.parent = report, report
        self.presample = self.parent.presample
        # Other #
        self.title = title

    def name(self):
        if 'USER_FULL_NAME' in os.environ: return os.environ['USER_FULL_NAME']
        else: return "Uppmax user ``%s''" % getpass.getuser()
    def status(self): return os.environ.get('USER_STATUS') or ""
    def company(self): return os.environ.get('USER_COMPANY') or ""
    def subcompany(self): return os.environ.get('USER_SUBCOMPANY') or ""
    def title(self): return self.title
    def image_left(self): return illumitag.module_dir + "reporting/common/ebc.png"
    def image_right(self): return illumitag.module_dir + "reporting/common/uu.png"

###############################################################################
class FooterTemplate(object):
    """All the parameters to be rendered in the LaTeX footer template"""
    pass

###############################################################################
class ScaledFigure(object):
    """A figure in latex code which can have its size adjusted"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, path, caption, label=None, **kwargs):
        self.path, self.caption = path, caption
        self.label = r"\label{" + label + "}\n" if label is not None else ''
        self.kwargs = kwargs

    def __str__(self):
        pystache.defaults.DELIMITERS = (u'@@[', u']@@')
        renderer = pystache.Renderer(escape=lambda u: u)
        return renderer.render(self)

    def path(self): return self.path
    def caption(self): return self.caption
    def label(self): return self.label
    def graph_params(self): return ','.join('%s=%s' % (k,v) for k,v in self.kwargs.items())

###############################################################################
class DualFigure(object):
    """A figure in latex code which has two subfigures"""

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, path_one, path_two, caption_one, caption_two, label_one, label_two, caption_main, label_main):
        self.path_one, self.path_two = path_one, path_two
        self.caption_one, self.caption_two = caption_one, caption_two
        self.label_one = r"\label{" + label_one + "}\n" if label_one is not None else ''
        self.label_two = r"\label{" + label_two + "}\n" if label_two is not None else ''
        self.caption_main = caption_main
        self.label_main = r"\label{" + label_main + "}\n" if label_main is not None else ''

    def __str__(self):
        pystache.defaults.DELIMITERS = (u'@@[', u']@@')
        renderer = pystache.Renderer(escape=lambda u: u)
        return renderer.render(self)

    def path_one(self): return self.path_one
    def path_two(self): return self.path_two
    def caption_one(self): return self.caption_one
    def caption_two(self): return self.caption_two
    def label_one(self): return self.label_one
    def label_two(self): return self.label_two
    def caption_main(self): return self.caption_main
