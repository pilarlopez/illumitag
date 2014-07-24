#!/usr/bin/env python2

"""
It might come in handy one day...
"""

def make_slurm_report(self):
    if not self.loaded: self.load()
    running_jobs_names = [j['name'] for j in slurm.running_jobs_info()]
    queued_jobs_names = [j['name'] for j in slurm.running_jobs_info()]
    for p in self:
        # Let's see if it didn't fail #
        p.job_state = "Failed"
        # Running #
        if str(p) in queued_jobs_names:
            p.job_state = "Queued"
            continue
        if str(p) in running_jobs_names:
            p.job_state = "Running"
            continue
        # Out path #
        job_out_path = p.runner.latest_log + 'run.out'
        # No file #
        if not os.path.exists(job_out_path):
            p.job_state = "Missing"
            continue
        # Read the log #
        with open(job_out_path, 'r') as handle: job_out = handle.read()
        # Success #
        if 'Success' in job_out: p.job_state = "Success"
        # Problems #
        if 'CANCELLED' in job_out: p.job_state = "Slurm CANCELLED"
        if '(core dumped)' in job_out: p.job_state = "Core DUMPED"
        # Start and end time #
        start_time = re.findall('^SLURM: start at (.+) on .+$', job_out, re.M)
        if start_time: p.runner.job_start_time = dateutil_parse(start_time[0])
        end_time = re.findall('^SLURM: end at (.+)$', job_out, re.M)
        if end_time: p.runner.job_end_time = dateutil_parse(end_time[0])
        # Total time #
        if start_time and end_time:
            p.runner.job_runtime = p.runner.job_end_time - p.runner.job_start_time
    # Make report #
    rows = [str(p) for p in self]
    columns = ['Name', 'Project', 'State', 'Start time', 'End time', 'Run time']
    data = [(p.long_name, p.project.name, p.job_state,
            str(p.runner.job_start_time), str(p.runner.job_end_time), str(p.runner.job_runtime))
            for p in self]
    frame = pandas.DataFrame(data, index=rows, columns=columns)
    frame.to_csv(self.p.slurm_report)

def make_zipfile(self):
    # Delete current report #
    if os.path.exists(self.p.report_zip): shutil.rmtree(self.p.report_zip)
    report_dir = self.base_dir + 'report/'
    if os.path.exists(report_dir): shutil.rmtree(report_dir)
    # Copy the experiment results dir #
    shutil.copytree(self.p.results_dir, report_dir)
    # Add the pool results #
    for p in self.pools:
        shutil.copytree(p.p.graphs_dir, report_dir + 'pool%i/' % p.num)
        #for g in l.groups:
        #    shutil.copytree(g.p.graphs_dir, report_dir + 'pool%i/' % l.num + g.short_name + '/')
    # Zip it #
    sh.tar('-zc', '-C', self.base_dir, '-f', self.p.report_zip, 'report')
    shutil.rmtree(report_dir)