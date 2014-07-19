# -*- coding: utf-8 -*-

# Built-in modules #

# Internal modules #
from illumitag.common import Password, md5sum, gps_deg_to_float
from illumitag.common.autopaths import AutoPaths

# Third party modules #
from ftputil import FTPHost

# Constants #
ftp_server = "ftp-private.ncbi.nih.gov"
ftp_login = "sra"
ftp_password = Password("ENA FTP password for user '%s':" % ftp_login)

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

    def upload_to_sra(self):
        # Print #
        print self.s.short_name
        # Connect #
        print "Connecting..."
        ftp = FTPHost(ftp_server, ftp_login, str(ftp_password))
        # Gzip if not there yet #
        if not self.s.raw_gz.exists:
            self.s.raw.fwd.gzip_to(self.s.p.raw_forward_gz)
            self.s.raw.rev.gzip_to(self.s.p.raw_reverse_gz)
        # Make directory #
        print "Making directories..."
        ftp.makedirs(self.directory)
        # Upload #
        base_path = self.directory + self.base_name
        print "Uploading forward..."
        ftp.upload(self.s.p.raw_forward_gz, base_path.format("forward"))
        print "Uploading reverse..."
        ftp.upload(self.s.p.raw_reverse_gz, base_path.format("reverse"))
        # Return #
        ftp.close()

    @property
    def biosample_line(self):
        """Will generate the corresponding BioSample entry"""
        # sample_name
        line = ["Soda lake %s (%s)" % (self.s.short_name, self.s.name)]
        # description
        line += [""]
        # bioproject_id
        line += ["PRJNA255501"]
        # sample_title
        line += [""]
        # organism
        line += ["aquatic metagenome"]
        # collection_date
        line += [self.s.info['date']]
        # collection_depth
        line += ["surface"]
        # env_biome, env_feature, env_material
        line += ["saline lake"]
        line += ["lake"]
        line += ["water"]
        # geo_loc_name, lat_lon
        line += ["Austria: " + self.s.info['real_name'][0]]
        # lat_lon
        coords = (gps_deg_to_float(self.s.info['GPS N'][0]), gps_deg_to_float(self.s.info['GPS E'][0]))
        line += ['{:7.6f} N {:7.6f} E'.format(*coords)]
        # Return #
        return line

    @property
    def fwd_md5(self): return md5sum(self.s.p.raw_forward_gz)
    @property
    def rev_md5(self): return md5sum(self.s.p.raw_reverse_gz)

###############################################################################
class PyroSampleSRA(object):

    def __init__(self, sample):
        self.s = sample
        self.directory = '/ILLUMITAG/pyrosamples/'
        self.name = self.s.short_name + '.sff'

    def upload_to_sra(self):
        # Print #
        print self.s.short_name
        # Connect #
        print "Connecting..."
        ftp = FTPHost(ftp_server, ftp_login, str(ftp_password))
        # Make directory #
        print "Making directories..."
        ftp.makedirs(self.directory)
        # Upload #
        dest_path = self.directory + self.name
        print "Uploading to '%s' (%s)..." % (dest_path, self.s.p.raw_sff.size)
        ftp.upload(self.s.p.raw_sff, dest_path)
        # Return #
        ftp.close()

    @property
    def base_name(self):
        class NoFormat(object):
            @classmethod
            def format(cls, _):
                return self.name
        return NoFormat()

    @property
    def fwd_md5(self): return md5sum(self.s.p.raw_sff)
    @property
    def rev_md5(self): return md5sum(self.s.p.raw_sff)

###############################################################################
class MakeSpreadsheet(object):
    """A class to generate the spreadsheets required by the NCBI/SRA
    raw data submission"""

    bioproject_accession    = None
    biosample_accession     = None
    sample_name             = None
    library_strategy        = "AMPLICON"
    library_source          = "METAGENOMIC"
    library_selection       = "PCR"
    library_layout          = "Paired-end"
    platform                = "ILLUMINA"
    instrument_model        = "Illumina MiSeq"
    forward_read_length     = "250"
    reverse_read_length     = "250"
    forward_filetype        = "fastq"
    reverse_filetype        = "fastq"

    all_paths = """
    /biosample_creation.tsv
    /sra_submission.tsv
    """

    header_sra =  ['bioproject_accession',
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
                   'MD5_checksum']

    header_bio = ['*sample_name',
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
                  '*lat_lon']

    def __init__(self, cluster):
        """You give a cluster as input"""
        # Base parameters #
        self.cluster = cluster
        self.samples = cluster.samples
        # Auto paths #
        self.base_dir = self.cluster.base_dir + 'sra/'
        self.p = AutoPaths(self.base_dir, self.all_paths)

    @property
    def lines(self):
        for s in self.samples:
            # accession
            line =  [s.info['bioproject']]
            line += [s.info['biosample']]
            # name
            line += [s.short_name]
            line += [s.short_name]
            # description
            machine = 'Illumina MiSeq' if 'machine' not in s.__dict__ else s.machine
            desc = "Soda lake '%s' (code %s) sampled on %s and run on a %s"
            desc += " -- run number %i, pool number %i, barcode number %i."
            line += [desc % (s.info['real_name'][0], s.short_name, s.info['date'],
                             machine, s.pool.run_num, s.pool.num, s.num)]
            # library_strategy
            line += [self.library_strategy, self.library_source, self.library_selection]
            line += [self.library_layout, self.platform, self.instrument_model]
            # design_description
            line += [s.pool.info['design_description']]
            # reference_genome_assembly
            line += ['', '']
            # forward_read_length
            line += [self.forward_read_length, self.reverse_read_length]
            # forward
            line += [self.forward_filetype, s.sra.base_name.format("forward")]
            line += [s.sra.fwd_md5]
            # reverse
            line += [self.reverse_filetype, s.sra.base_name.format("reverse")]
            line += [s.sra.rev_md5]
            # write
            yield line

    def write_sra_tsv(self):
        """Will write the appropriate TSV for the SRA submission in the cluster directory"""
        header = '\t'.join(self.header_sra) + '\n'
        content = '\n'.join('\t'.join(l) for l in self.lines)
        self.p.submission.write(header+content, 'windows-1252')

    def write_bio_tsv(self):
        """Will write the TSV required by the NCBI for the creation of 'BioSample' objects"""
        header = '\t'.join(self.header_bio) + '\n'
        content = '\n'.join('\t'.join(s.sra.biosample_line) for s in self.samples)
        self.p.biosample.write(header+content, 'utf-8')
