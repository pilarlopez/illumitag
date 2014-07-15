# Built-in modules #

# Internal modules #
from illumitag.common import Password, md5sum

# Third party modules #
from ftputil import FTPHost

# Constants #
ftp_server = "webin.ebi.ac.uk"
ftp_login = "Webin-38108"
ftp_password = Password("ENA FTP password for user '%s':" % ftp_login)

###############################################################################
class SampleENA(object):
    """Every sample has an instance of this class, which enables us to
    access ENA required parameters for every sample"""

    def __init__(self, sample):
        self.s = sample
        self.directory = '/ILLUMITAG/run%03d/pool%02d/sample%02d/'
        self.directory = self.directory % (self.s.pool.run_num, self.s.pool.num, self.s.num)
        self.base_name = 'run%03d_pool%02d_sample%02d_{}_reads.fastq.gz'
        self.base_name = self.base_name % (self.s.pool.run_num, self.s.pool.num, self.s.num)

    def upload_to_ena(self):
        # Connect #
        print "Connecting..."
        ftp = FTPHost(ftp_server, ftp_login, str(ftp_password))
        # Gzip if not there yet #
        if not self.raw_gz.exists:
            self.raw.fwd.gzip_to(self.p.raw_forward_gz)
            self.raw.rev.gzip_to(self.p.raw_reverse_gz)
        # Make directory #
        directory = '/ILLUMITAG/run%03d/pool%02d/sample%02d/'
        directory = directory % (self.pool.run_num, self.pool.num, self.num)
        print "Making directories..."
        ftp.makedirs(directory)
        # Upload #
        base_path = directory + 'run%03d_pool%02d_sample%02d_{}_reads.fastq.gz'
        base_path = base_path % (self.pool.run_num, self.pool.num, self.num)
        print "Uploading forward..."
        ftp.upload(self.p.raw_forward_gz, base_path.format("forward"))
        print "Uploading reverse..."
        ftp.upload(self.p.raw_reverse_gz, base_path.format("reverse"))
        # Return #
        ftp.close()

    @property
    def sample_parameters(self):
        """Generate the 'sample' required parameters for submitting this sample to ENA"""
        default_description = "This is a sample that is part of the '%s' project. It comes from the run number %i at the sequencing facility where it was part of the pool number %i. The corresponding barcode it had was number %i."
        default_description = default_description % (self.s.pool.project.name, self.s.pool.run_num, self.s.pool.num, self.s.num)
        return {
            'unique_name':        self.s.name,
            'sample_title':       self.s.short_name,
            'sample_description': default_description,
            'run_num':            self.s.pool.run_num,
            'pool_num':           self.s.pool.num,
            'barcode_num':        self.s.num,
            'barcode_fwd':        self.s.fwd_str,
            'barcode_rev':        self.s.rev_str,
            'group_name':         self.s.group_name,
        }

    @property
    def experiment_parameters(self):
        """Generate the 'experiment' required parameters for submitting this sample to ENA"""
        default_description = "This is the experiment corresponding to a sample that is part of the '%s' project. It comes from the run number %i at the sequencing facility where it was part of the pool number %i. The corresponding barcode it had was number %i."
        default_description = default_description % (self.s.pool.project.name, self.s.pool.run_num, self.s.pool.num, self.s.num)
        return {
            'unique_name':        "experiment_" + self.s.name,
            'experiment_title':   "experiment_" + self.s.short_name,
            'design_description': default_description,
            'sample_name':        self.s.name,
            'library_name':       "library_" + self.s.name,
        }

    @property
    def run_parameters(self):
        """Generate the 'run' required parameters for submitting this sample to ENA"""
        return {
            'unique_name':        "run" + self.s.name,
            'experiment_name':    "experiment_" + self.s.short_name,
            'fwd_filename':       self.base_name.format('forward'),
            'fwd_checksum':       md5sum(self.s.p.raw_forward_gz),
            'rev_filename':       self.base_name.format('reverse'),
            'rev_checksum':       md5sum(self.s.p.raw_reverse_gz),
        }

###############################################################################
class MakeAllXML(object):
    """A class to generate the five XML documents necessary for an automatic Submission
    These are: Submission, Study, Sample, Experiment and Run XML"""

    def __init__(self, project, cluster):
        """You give a project and cluster as input"""
        self.cluster         = cluster
        self.project         = project
        self.samples         = cluster.samples
        self.sub_unique_name = self.project.name
        self.center_name     = "Limnology department at Uppsala University"
        self.study_title     = self.project.title
        self.study_abstract  = self.project.abstract

    #-------------------------------------------------------------------------#
    template_submission = """<?xml version="1.0" encoding="UTF-8"?>
<SUBMISSION_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.submission.xsd">
<SUBMISSION alias="%(unique_name)s"
 center_name="%(center_name)s">
        <ACTIONS>
            <ACTION>
                <ADD source="%(study)s" schema="study"/>
            </ACTION>
            <ACTION>
                <ADD source="%(sample)s" schema="sample"/>
            </ACTION>
            <ACTION>
                <ADD source="%(experiment)s" schema="experiment"/>
            </ACTION>
            <ACTION>
                <ADD source="%(run)s" schema="run"/>
            </ACTION>
            <ACTION>
                <ADD source="%(analysis)s" schema="analysis"/>
            </ACTION>
            <ACTION>
                <HOLD HoldUntilDate="2016-07-13"/>
            </ACTION>
        </ACTIONS>
    </SUBMISSION>
</SUBMISSION_SET>"""

    @property
    def xml_submission(self):
        """Returns the Submission XML document"""
        params = {'unique_name': self.sub_unique_name,
                  'center_name': self.center_name,
                  'study': '',
                  'sample': '',
                  'experiment': '',
                  'run': '',
                  'analysis': '',
        }
        return self.template_submission%params

    #-------------------------------------------------------------------------#
    template_study = """<?xml version="1.0" encoding="UTF-8"?>
<STUDY_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.study.xsd">
    <STUDY alias="%(unique_name)s"
        center_name="%(center_name)s">
        <DESCRIPTOR>
            <STUDY_TITLE>%(study_title)s</STUDY_TITLE>
            <STUDY_TYPE existing_study_type="Metagenomics"/>
            <STUDY_ABSTRACT>%(study_abstract)s</STUDY_ABSTRACT>
        </DESCRIPTOR>
        <STUDY_ATTRIBUTES>
        </STUDY_ATTRIBUTES>
    </STUDY>
</STUDY_SET>"""

    @property
    def xml_study(self):
        """Returns the Study XML document"""
        params = {'unique_name': self.sub_unique_name,
                  'center_name': self.center_name,
                  'study_title': self.study_title,
                  'study_abstract': self.study_abstract,
        }
        return self.template_study%params

    #-------------------------------------------------------------------------#
    template_all_sample = """<?xml version="1.0" encoding="UTF-8"?>
<SAMPLE_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.sample.xsd">%s</SAMPLE_SET>"""

    template_one_sample = """
    <SAMPLE alias="%(unique_name)s"
        center_name="%(center_name)s">
        <TITLE>%(sample_title)s</TITLE>
        <SAMPLE_NAME>
            <TAXON_ID>%(taxon_num)s</TAXON_ID>
            <SCIENTIFIC_NAME>%(taxon_long_name)s</SCIENTIFIC_NAME>
            <COMMON_NAME>%(taxon_short_name)s</COMMON_NAME>
        </SAMPLE_NAME>
        <DESCRIPTION>%(sample_description)s</DESCRIPTION>
        <SAMPLE_ATTRIBUTES>
            <SAMPLE_ATTRIBUTE>
                <TAG>Run number</TAG>
                <VALUE>%(run_num)s</VALUE>
            </SAMPLE_ATTRIBUTE>
            <SAMPLE_ATTRIBUTE>
                <TAG>Pool number</TAG>
                <VALUE>%(pool_num)s</VALUE>
            </SAMPLE_ATTRIBUTE>
            <SAMPLE_ATTRIBUTE>
                <TAG>Barcode number</TAG>
                <VALUE>%(barcode_num)s</VALUE>
            </SAMPLE_ATTRIBUTE>
            <SAMPLE_ATTRIBUTE>
                <TAG>Forward barcode</TAG>
                <VALUE>%(barcode_fwd)s</VALUE>
            </SAMPLE_ATTRIBUTE>
            <SAMPLE_ATTRIBUTE>
                <TAG>Reverse barcode</TAG>
                <VALUE>%(barcode_rev)s</VALUE>
            </SAMPLE_ATTRIBUTE>
            <SAMPLE_ATTRIBUTE>
                <TAG>Sample grouping name</TAG>
                <VALUE>%(group_name)s</VALUE>
            </SAMPLE_ATTRIBUTE>
        </SAMPLE_ATTRIBUTES>
    </SAMPLE>"""

    @property
    def xml_sample(self):
        """Returns the Sample XML document"""
        all_xml = []
        for sample in self.samples:
            params = sample.ena.sample_parameters
            params['center_name'] = self.center_name
            params['taxon_num'] = '256318'
            params['taxon_long_name'] = 'metagenome'
            params['taxon_short_name'] = 'metagenome'
            all_xml.append(self.template_one_sample % params)
        return self.template_all_sample % ('\n'.join(all_xml))

    #-------------------------------------------------------------------------#
    template_all_experiment = """<?xml version="1.0" encoding="UTF-8"?>
<EXPERIMENT_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.experiment.xsd">%s</EXPERIMENT_SET>"""

    template_one_experiment = """
    <EXPERIMENT alias="%(unique_name)s"
        center_name="%(center_name)s">
        <TITLE>%(experiment_title)s</TITLE>
        <STUDY_REF refname="%(study_name)s"/>
        <DESIGN>
            <DESIGN_DESCRIPTION>%(design_description)s</DESIGN_DESCRIPTION>
            <SAMPLE_DESCRIPTOR refname="%(sample_name)s"/>
            <LIBRARY_DESCRIPTOR>
                <LIBRARY_NAME>%(library_name)s</LIBRARY_NAME>
                <LIBRARY_STRATEGY>%(library_strategy)s</LIBRARY_STRATEGY>
                <LIBRARY_SOURCE>%(library_source)s</LIBRARY_SOURCE>
                <LIBRARY_SELECTION>%(library_selection)s</LIBRARY_SELECTION>
                <LIBRARY_LAYOUT>
                    <PAIRED NOMINAL_LENGTH="%(expected_insert_size)s"/>
                </LIBRARY_LAYOUT>
                <LIBRARY_CONSTRUCTION_PROTOCOL>%(library_protocol)s</LIBRARY_CONSTRUCTION_PROTOCOL>
            </LIBRARY_DESCRIPTOR>
        </DESIGN>
        <PLATFORM>
            <ILLUMINA>
                <INSTRUMENT_MODEL>%(illumina_model)s</INSTRUMENT_MODEL>
            </ILLUMINA>
        </PLATFORM>
        <PROCESSING/>
    </EXPERIMENT>"""

    @property
    def xml_experiment(self):
        """Returns the Experiment XML document"""
        all_xml = []
        for sample in self.samples:
            params = sample.experiment_parameters
            params['center_name'] = self.center_name
            params['study_name'] = self.sub_unique_name
            params['library_strategy'] = "AMPLICON"
            params['library_source'] = "METAGENOMIC"
            params['library_selection'] = "PCR"
            params['expected_insert_size'] = str(805 - 341)
            params['library_protocol'] = "TruSeq"
            params['illumina_model'] = "Illumina MiSeq"
            all_xml.append(self.template_one_experiment % params)
        return self.template_all_experiment % ('\n'.join(all_xml))

    #-------------------------------------------------------------------------#
    template_all_run = """<?xml version="1.0" encoding="UTF-8"?>
<RUN_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.run.xsd">%s</RUN_SET>"""

    template_one_run = """<RUN alias="%(unique_name)s" center_name="%(center_name)s" run_date="%(run_date)sT00:00:00">
        <EXPERIMENT_REF refname="%(experiment_name)s"/>
         <DATA_BLOCK>
            <FILES>
                <FILE filename="%(fwd_filename)s"
                    filetype="fastq" checksum_method="MD5" checksum="%(fwd_checksum)s"/>
                <FILE filename="%(rev_filename)s"
                    filetype="fastq" checksum_method="MD5" checksum="%(rev_checksum)s"/>
            </FILES>
        </DATA_BLOCK>
    </RUN>"""

    @property
    def xml_run(self):
        """Returns the Run XML document"""
        all_xml = []
        for sample in self.samples:
            params = sample.run_parameters
            params['center_name'] = self.center_name
            params['run_date'] = self.sub_unique_name
            all_xml.append(self.template_one_run % params)
        return self.template_all_run % ('\n'.join(all_xml))

    #-------------------------------------------------------------------------#
    def write_files(self):
        """Will write the five files in the cluster directory"""
        directory = self.cluster.base_dir
        pass
