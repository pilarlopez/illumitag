# Built-in modules #
import os, shutil

# Internal modules #
from plumbing.autopaths import AutoPaths
from plumbing.slurm import nr_threads
from plumbing.csv_tables import CSVTable
from plumbing.tmpstuff import TmpFile

# Third party modules #
import pandas, sh
from Bio import SeqIO

# Constants #
home = os.environ['HOME'] + '/'
seqenv_script = home + "share/seqenv/SEQenv_v0.8/SEQenv_samples.sh"

###############################################################################
class Seqenv(object):
    """Base class for Seqenv results processing."""
    N = 5000

    all_paths = """
    /working_dir/
    /working_dir/seqenv.out
    /working_dir/seqenv.err
    /abundances.csv
    """

    @property
    def files_to_keep(self):
        return [
            "centers_N%i_blast_F_ENVO_OTUs.csv" % self.N,
            "centers_N%i_blast_F_ENVO_OTUs_labels.csv" % self.N,
            "centers_N%i_blast_F_ENVO_samples_labels.csv" % self.N,
        ]

    def __init__(self, parent, base_dir=None):
        # Parent #
        self.otu, self.parent = parent, parent
        self.taxonomy = self.parent.taxonomy
        # Inherited #
        self.samples = self.parent.samples
        # Dir #
        if base_dir is None: self.base_dir = self.parent.p.seqenv_dir
        else: self.base_dir = base_dir
        self.p = AutoPaths(self.base_dir, self.all_paths)
        # Files #
        self.abundances = CSVTable(self.p.abundances)

    def run(self, threshold=3.0, cleanup=True, N=None):
        # Change the N #
        if N != None: self.N = N
        # Clean up #
        if cleanup:
            shutil.rmtree(self.p.working_dir)
            for f in self.files_to_keep: os.remove(self.base_dir + f) if os.path.exists(self.base_dir + f) else None
        # Move to the working dir #
        self.saved_cwd = os.getcwd()
        os.chdir(self.p.working_dir)
        # Make the abundances file #
        self.taxonomy.otu_csv_norm.transpose(self.abundances, d=',')
        # Make the most abundant OTU file (launching one perl command per OTU sequence takes forever) #
        path = "centers_N%i.fa" % self.N
        if len(self.taxonomy.centers) <= self.N: self.taxonomy.centers.copy(path)
        else:
            otus = self.taxonomy.otu_table_norm.sum()
            otus.sort()
            highest_otus = otus[-self.N:]
            sequences = (seq for seq in SeqIO.parse(self.taxonomy.centers, 'fasta') if seq.id in highest_otus)
            with open(path, 'w') as handle: SeqIO.write(sequences, handle, 'fasta')
        # Run the Quince pipeline with a special version of R #
        header = 'module load R/3.0.1' + '\n'
        header += 'export R_LIBS="$HOME/R/x86_64-unknown-linux-gnu-library/3.0/"' + '\n'
        header += 'unset R_HOME' + '\n'
        # Log standard out and standard error as well as both together #
        tee = "((%s | tee stdout.log) 3>&1 1>&2 2>&3 | tee stderr.log) &> stdboth.log"
        # See seqenv documentation for parameters #
        identity = 100 - threshold
        params = ['-f', self.taxonomy.centers, '-s', self.abundances, '-n', self.N, '-m', identity, '-p', '-c', nr_threads]
        # Activate bash debug mode #
        command = "bash -x " + seqenv_script + ' ' + ' '.join(map(str, params))
        # Launch the whole thing with sh #
        self.script = header + tee % command
        sh.bash(TmpFile.from_string(self.script), _out=self.p.out, _err=self.p.err)
        # Move things into place #
        if cleanup:
            for f in self.files_to_keep: shutil.move(f, "../")
        # Go back #
        os.chdir(self.saved_cwd)

    @property
    def frame(self):
        return pandas.io.parsers.read_csv(self.p.labels, sep=',', index_col=0, encoding='utf-8')