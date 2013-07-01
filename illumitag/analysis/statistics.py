# Built-in modules #
import itertools

# Internal modules #
from illumitag.common.tmpstuff import TmpFile

# Third party modules #
import sh
from rpy2 import robjects as ro

# Constants #

###############################################################################
class StatsOnOTU(object):

    all_paths = """
    /nmds/by_barcode.pdf
    /nmds/by_pool.pdf
    /nmds/by_run.pdf
    /nmds/r.out
    /permanova/all.txt
    /permanova/pairs.txt
    /beta_dispersion/permutest.txt
    /beta_dispersion/anova.txt
    /beta_dispersion/pool_plots.pdf
    /beta_dispersion/run_plots.pdf
    """

    def nmds(self):
        # Script #
        script = []
        # Load libs #
        script += ["library(vegan)"]
        script += ["library(MASS)"]
        script += ["library(ggplot2)"]
        script += ["library(compare)"]
        # Load data #
        script += ["data = read.table('%s', header=TRUE, sep='\t', row.names='OTUID')" % (self.p.table_trimmed)]
        script += ["meta = read.table('%s', header=TRUE, sep='\t', row.names=1)" % (self.procedure.metadata_path)]
        # Compute nmds #
        script += ["ord = metaMDS(data, distance='%s', trymax=200)" % self.dist_method]
        script += ["nmds = scores(ord)"]
        # Make a dataframe #
        script += ["df = merge(meta, nmds, by.x='row.names', by.y='row.names')"]
        # Make factors #
        script += ["df$barcode = factor(df$barcode)"]
        script += ["df$run = factor(df$run)"]
        script += ["df$pool = factor(df$pool)"]
        # Make plots #
        script += ["p = ggplot(df, aes(NMDS1, NMDS2)) + xlab('Dimension 1') + ylab('Dimension 2')"]
        script += ["pdf(file='%s')" % self.p.nmds_by_barcode]
        script += ["p + geom_point(aes(colour=barcode))"]
        script += ["dev.off()"]
        script += ["pdf(file='%s')" % self.p.nmds_by_pool]
        script += ["p + geom_point(aes(colour=pool))"]
        script += ["dev.off()"]
        script += ["pdf(file='%s')" % self.p.nmds_by_run]
        script += ["p + geom_point(aes(colour=run))"]
        script += ["dev.off()"]
        # Run it #
        sh.R('--no-save', '-f', TmpFile.from_string('\n'.join(script)), _out=self.p.nmds_out)

    def permanova(self):
        # Basic PERMANOVA #
        ro.r("library(vegan)")
        ro.r("data = read.table('%s', header=TRUE, sep='\t', row.names='OTUID')" % (self.p.table_trimmed))
        ro.r("meta = read.table('%s', header=TRUE, sep='\t', row.names=1)" % (self.procedure.metadata_path))
        ro.r("data_ordered = data[order(row.names(data)),]")
        ro.r("meta_ordered = meta[row.names(data),]")
        ro.r("meta_ordered = meta_ordered[order(row.names(meta_ordered)),]")
        # As factor #
        ro.r("meta_ordered$pool = factor(meta_ordered$pool)")
        ro.r("meta_ordered$barcode = factor(meta_ordered$barcode)")
        ro.r("meta_ordered$run = factor(meta_ordered$run)")
        # Run test #
        ro.r("permanova = adonis(formula = data ~ pool * barcode, data=meta_ordered, permutations=1000, method='%s')" % self.dist_method)
        result = '\n'.join(ro.r("capture.output(print(permanova))")).encode('utf-8')
        with open(self.p.permanova_all, 'w') as handle: handle.write(result)
        # All pool pairs #
        with open(self.p.permanova_pairs, 'w') as handle:
            for pair in itertools.combinations(['1', '2', '3', '4', '5'], 2):
                ro.r("subset = row.names(meta_ordered[meta_ordered$pool == 1 | meta_ordered$pool == 3,])")
                ro.r("subdata = data_ordered[subset,]")
                ro.r("submeta = meta_ordered[subset,]")
                ro.r("permanova = adonis(formula = subdata ~ pool * barcode, data=submeta, permutations=1000, method='%s')" % self.dist_method)
                handle.write("\n\n ---- Pool %s against Pool %s ---- \n\n" % pair)
                result = '\n'.join(ro.r("capture.output(print(permanova))")).encode('utf-8')
                handle.write(result)

    def beta_dispersion(self):
        # Prepare #
        ro.r("library(vegan)")
        ro.r("data = read.table('%s', header=TRUE, sep='\t', row.names='OTUID')" % (self.p.table_trimmed))
        ro.r("meta = read.table('%s', header=TRUE, sep='\t', row.names=1)" % (self.procedure.metadata_path))
        # Compute #
        ro.r("data_ordered = data[order(row.names(data)),]")
        ro.r("data_sqrt = sqrt(data_ordered)")
        ro.r("data_wa = wisconsin(data_sqrt)")
        ro.r("data_dist = vegdist(data_wa, method='%s')" % self.dist_method)
        ro.r("meta = meta[row.names(data),]")
        ro.r("pool = factor(meta[,1])")
        ro.r("run = factor(meta[,3])")
        # Run group #
        ro.r("mod1 = betadisper(data_dist, run)")
        ro.r("test = permutest(mod1, control = permControl(nperm = 1000))")
        result = '\n'.join(ro.r("capture.output(print(test))")).encode('utf-8')
        with open(self.p.beta_dispersion_permutest, 'w') as handle: handle.write(result)
        ro.r("test = anova(mod1)")
        result = '\n'.join(ro.r("capture.output(print(test))")).encode('utf-8')
        with open(self.p.beta_dispersion_anova, 'w') as handle: handle.write(result)
        ro.r("pdf(file='%s')" % self.p.beta_dispersion_run_plots)
        ro.r("plot(mod1)")
        ro.r("boxplot(mod1)")
        ro.r("plot(TukeyHSD(mod1))")
        ro.r("dev.off()")
        # Pool group #
        ro.r("mod2 = betadisper(data_dist, pool)")
        ro.r("test = permutest(mod2, control = permControl(nperm = 1000))")
        result = '\n'.join(ro.r("capture.output(print(test))")).encode('utf-8')
        with open(self.p.beta_dispersion_permutest, 'w') as handle: handle.write(result)
        ro.r("mod1 = betadisper(data_dist, run)")
        ro.r("test = anova(mod2)")
        result = '\n'.join(ro.r("capture.output(print(test))")).encode('utf-8')
        with open(self.p.beta_dispersion_anova, 'w') as handle: handle.write(result)
        ro.r("pdf(file='%s')" % self.p.beta_dispersion_pool_plots)
        ro.r("plot(mod2)")
        ro.r("boxplot(mod2)")
        ro.r("plot(TukeyHSD(mod2))")
        ro.r("dev.off()")