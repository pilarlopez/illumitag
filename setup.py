from distutils.core import setup

setup(
      name             = 'illumitag',
      version          = '1.0.2',
      description      = 'Pipeline for 16S Illumina paired-end sequencing',
      long_description = open('README.md').read(),
      license          = 'MIT',
      url              = 'http://github.com/limno/illumitag/',
      author           = 'Lucas Sinclair',
      author_email     = 'lucas.sinclair@me.com',
      classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
      packages         = ['illumitag'],
      requires         = ['plumbing', 'fasta', 'sh', 'biopython', 'matplotlib', 'threadpool', 'patsy', 'pandas', 'statsmodels', 'rpy2', 'scikit-learn', 'rpy2', 'brewer2mpl', 'regex', 'ftputil', 'names', 'shell_command', 'pystache', 'tabulate', 'tqdm', 'scikit-bio==0.1.4'],
)