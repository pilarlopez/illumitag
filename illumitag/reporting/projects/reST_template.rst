Project "{{sample_short_name}}"
==============================

General Information
-------------------


Clustering
----------
Two sequences that diverge by no more than a few nucleotides are probably not produced by ecological diversity. They are most likely produced by errors along the laboratory method. So we put them together in one cluster, called an OTU. A sequence that does not have any such similar-looking brothers is most likely the product of a recombination (chimera) and is discarded. This result in the creation an OTU table which is too big to view directly. However we can plot some of its properties:

Classification
--------------
Relying on the databases of ribosomal genes such as Silva, we can classify each cluster and give it an approximative affiliation. This provides a taxonomic name to each OTU. We can make more pretty graphs

Diversity
---------
We can compute estimators of diversity within the sample:


Comparison
----------
Using the other samples included in the same project (45 samples) we can start comparing this sample to the others. A first simple means of doing that is plotting them on an ordination plot.
