# Built-in modules #

# Internal modules #
from illumitag.running import Runner
from illumitag.common.slurm import SLURMJob

# Third party modules #

# Constants #

###############################################################################
class ClusterRunner(Runner):
    """Will run stuff on an cluster"""
    default_time = '1-00:00:00'

    default_steps = [
        ### Start ###
        {'process_samples':           {}},
        {'combine_reads':             {}},
        ### OTUs ###
        {'run_uparse':                {}},
        ### Taxonomy ###
        {'otu_uparse.taxonomy_silva.assign':                        {}},
        {'otu_uparse.taxonomy_silva.make_otu_table':                {}},
        {'otu_uparse.taxonomy_silva.make_otu_table_norm':           {}},
        {'otu_uparse.taxonomy_silva.make_plots':                    {}},
        {'otu_uparse.taxonomy_silva.stats.nmds.run':                {}},
        {'otu_uparse.taxonomy_silva.comp_phyla.make_taxa_table':    {}},
        {'otu_uparse.taxonomy_silva.comp_phyla.make_plots':         {}},
        {'otu_uparse.taxonomy_silva.comp_phyla.stats.nmds.run':     {}},
        {'otu_uparse.taxonomy_silva.comp_tips.make_taxa_table':     {}},
        {'otu_uparse.taxonomy_silva.comp_tips.make_plots':          {}},
        ### Source ###
        {'otu_uparse.seqenv.run':            {}},
    ]

    def __init__(self, parent):
        # Save parent #
        self.parent, self.cluster = parent, parent
        self.samples = parent.samples

    def run_slurm(self, steps=None, **kwargs):
        # Test case #
        if self.cluster.name == 'test':
            kwargs['time'] = '01:00:00'
            kwargs['email'] = '/dev/null'
        # Make script #
        command =  ["steps = %s" % steps]
        command += ["name = '%s'" % self.cluster.name]
        command += ["cluster = getattr(illumitag.clustering.favorites, name)"]
        command += ["cluster.run(steps)"]
        # Send it #
        if 'time' not in kwargs: kwargs['time'] = self.default_time
        if 'email' not in kwargs: kwargs['email'] = None
        if 'dependency' not in kwargs: kwargs['dependency'] = 'singleton'
        job_name = "cluster_%s" % self.cluster.name
        self.parent.slurm_job = SLURMJob(command, self.parent.p.logs_dir, job_name=job_name, **kwargs)
        return self.parent.slurm_job.run()