# -*- coding: utf-8 -*-

"""
Start with a BioProject creation here:
https://submit.ncbi.nlm.nih.gov/subs/bioproject/

Then the BioSamples (use the first TSV):
https://submit.ncbi.nlm.nih.gov/subs/biosample/

Finally a new submission here:
http://trace.ncbi.nlm.nih.gov/Traces/sra_sub/sub.cgi

And email the second TSV to the support there:
sra@ncbi.nlm.nih.gov
"""

# Internal modules #
from plumbing import Password, md5sum, gps_deg_to_float
from plumbing.autopaths import AutoPaths

# Third party modules #
from ftputil import FTPHost

# Constants #
ftp_server = "ftp-private.ncbi.nih.gov"
ftp_login = "sra"
ftp_password = Password("SRA FTP password for user '%s':" % ftp_login)

# Lists #
header_bio = [
    '*sample_name',
    'description',
    'bioproject_id',
    'sample_title',
    '*organism',
    '*collection_date',
    '*depth',
    '*env_biome',
    '*env_feature',
    '*env_material',
    '*geo_loc_name',
    '*lat_lon',
]

header_sra =  [
    'bioproject_accession',
    'biosample_accession',
    'sample_name',
    'library_ID',
    'title/short description',
    'library_strategy',
    'library_source',
    'library_selection',
    'library_layout',
    'platform',
    'instrument_model',
    'design_description',
    'reference_genome_assembly',
    'alignment_software',
    'forward_read_length',
    'reverse_read_length',
    'filetype',
    'filename',
    'MD5_checksum',
    'filetype',
    'filename',
    'MD5_checksum',
]

default_bio = {
    'bioproject_id'        : "PRJNA000000",
    'organism'             : "aquatic metagenome",
    'depth'                : "surface",
    'env_biome'            : "river",
    'env_feature'          : "river",
    'env_material'         : "water",
}

default_sra = {
    'library_strategy'        : "AMPLICON",
    'library_source'          : "METAGENOMIC",
    'library_selection'       : "PCR",
    'library_layout'          : "Paired-end",
    'platform'                : "ILLUMINA",
    'instrument_model'        : "Illumina MiSeq",
    'forward_read_length'     : "250",
    'reverse_read_length'     : "250",
    'forward_filetype'        : "fastq",
    'reverse_filetype'        : "fastq",
}

###############################################################################
class SampleSRA(object):
    """Every sample has an instance of this class, which enables us to
    access SRA required parameters for every sample."""

    def __init__(self, sample):
        self.s = sample
        self.directory = '/ILLUMITAG/run%03d/pool%02d/sample%02d/'
        self.directory = self.directory % (self.s.pool.run_num, self.s.pool.num, self.s.num)
        self.base_name = 'run%03d_pool%02d_sample%02d_{}_reads.fastq.gz'
        self.base_name = self.base_name % (self.s.pool.run_num, self.s.pool.num, self.s.num)

    def upload_to_sra(self, verbose=True):
        """They have an FTP site where you should drop the files first"""
        # Print #
        if verbose: print self.s.short_name + ' (' + self.s.name + ')'
        # Connect #
        if verbose: print "Connecting..."
        ftp = FTPHost(ftp_server, ftp_login, str(ftp_password))
        # Gzip if not there yet #
        if not self.s.raw_gz.exists:
            self.s.raw.fwd.gzip_to(self.s.p.raw_forward_gz)
            self.s.raw.rev.gzip_to(self.s.p.raw_reverse_gz)
        # Make directory #
        if verbose: print "Making directories..."
        ftp.makedirs(self.directory)
        # Upload #
        base_path = self.directory + self.base_name
        if verbose: print "Uploading forward..."
        ftp.upload(self.s.p.raw_forward_gz, base_path.format("forward"))
        if verbose: print "Uploading reverse..."
        ftp.upload(self.s.p.raw_reverse_gz, base_path.format("reverse"))
        # Return #
        ftp.close()

    @property
    def biosample_line(self):
        """Will generate the corresponding BioSample entry"""
        # sample_name
        line = ["Sample %s (%s)" % (self.s.short_name, self.s.name)]
        # description
        line += [""]
        # bioproject_id
        line += default_bio['bioproject_id']
        # sample_title
        line += [""]
        # organism
        line += default_bio["organism"]
        # collection_date
        line += [self.s.info['date']]
        # depth
        line += default_bio["depth"]
        # env_biome, env_feature, env_material
        line += default_bio["env_biome"]
        line += default_bio["env_feature"]
        line += default_bio["env_material"]
        # geo_loc_name
        line += ["%s: %s" % (self.s.info['country'], self.s.info['real_name'])]
        # lat_lon
        coords = (gps_deg_to_float(self.s.info['GPS N'][0]), # Latitude
                  gps_deg_to_float(self.s.info['GPS E'][0])) # Longitude
        line += ['{:7.6f} N {:7.6f} E'.format(*coords)]
        # Return #
        return line

    @property
    def sra_line(self):
        """Will generate the corresponding entry for SRA submission"""
        # accession
        line =  [self.s.info['bioproject']]
        line += [self.s.info['biosample']]
        # name
        line += [self.s.short_name]
        line += [self.s.short_name]
        # description
        machine = 'Illumina MiSeq' if 'machine' not in self.s.__dict__ else self.s.machine
        desc = "Soda lake '%s' (code %s) sampled on %s and run on a %s"
        desc += " -- run number %i, pool number %i, barcode number %i."
        line += [desc % (self.s.info['real_name'][0], self.s.short_name, self.s.info['date'],
                         machine, self.s.pool.run_num, self.s.pool.num, self.s.num)]
        # library_strategy
        line += [default_sra['library_strategy']]
        line += [default_sra['library_source']]
        line += [default_sra['library_selection']]
        line += [default_sra['library_layout']]
        line += [default_sra['platform']]
        line += [default_sra['instrument_model']]
        # design_description
        line += [self.s.pool.info['design_description']]
        # reference_genome_assembly
        line += ['', '']
        # forward_read_length
        line += [self.forward_read_length, self.reverse_read_length]
        # forward
        line += [default_sra['forward_filetype'], self.base_name.format("forward")]
        line += [md5sum(self.s.p.raw_forward_gz)]
        # reverse
        line += [default_sra['reverse_filetype'], self.base_name.format("reverse")]
        line += [md5sum(self.s.p.raw_reverse_gz)]
        # return
        return line

###############################################################################
class MakeSpreadsheet(object):
    """A class to generate the spreadsheets required by the NCBI/SRA
    for raw data submission"""

    all_paths = """
    /biosample_creation.tsv
    /sra_submission.tsv
    """

    def __init__(self, cluster):
        """You give a cluster as input"""
        # Base parameters #
        self.cluster = cluster
        self.samples = cluster.samples
        # Auto paths #
        self.base_dir = self.cluster.base_dir + 'sra/'
        self.p = AutoPaths(self.base_dir, self.all_paths)

    def write_bio_tsv(self):
        """Will write the TSV required by the NCBI for the creation of 'BioSample' objects"""
        header = '\t'.join(header_bio) + '\n'
        content = '\n'.join('\t'.join(s.sra.biosample_line_danube) for s in self.samples)
        self.p.biosample.write(header+content, 'utf-8')

    def write_sra_tsv(self):
        """Will write the appropriate TSV for the SRA submission in the cluster directory"""
        header = '\t'.join(header_sra) + '\n'
        content = '\n'.join('\t'.join(s.sra.sra_line_danube) for s in self.samples)
        self.p.sra.write(header+content, 'windows-1252')
