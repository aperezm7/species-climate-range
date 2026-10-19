# Why the model uses only BIO1 and BIO12

WorldClim 2.1 publishes 19 bioclimatic variables. This model uses two:

| Variable | Meaning | Units after this repo scales them |
| --- | --- | --- |
| BIO1 | Annual mean temperature | °C |
| BIO12 | Annual precipitation | mm |

Official WorldClim temperature GeoTIFFs are stored as degrees Celsius times 10. The live loader divides BIO1 by 10. BIO12 is already millimetres. The fixture grids are written in those real units.

BIO1 and BIO12 are the energy axis and the water axis. They are the coarsest climate summary that still answers "where is it warm and wet enough?" A jaguar model that stopped here is incomplete as ecology. It is complete enough to score a cell, and it does not pretend that 19 collinear layers are 19 independent facts.

The 10-arc-minute float grids from the WorldClim 2.1 archive used here already store BIO1 in °C. Older integer WorldClim files store temperature as °C × 10. The loader divides BIO1 by 10 only when the absolute values in the crop exceed 80, which is that integer encoding. BIO12 stays in millimetres either way. The synthetic fixture is written in real units and is not passed through this check.

## What a fuller stack has to earn

The temperature family moves together. Annual mean temperature (BIO1), the warmest and coldest months (BIO5, BIO6), and the means of the warmest and coldest quarters (BIO10, BIO11) are different views of the same seasonal cycle. The precipitation family does the same thing: annual precipitation (BIO12), the wettest month (BIO13), and the wettest quarter (BIO16) often describe one gradient.

A boosted tree can still split those columns. The split it picks is unstable. Importance then jumps between variables that carry the same information, and a response curve can credit a quarter that is only a stand-in for the annual mean. Dormann and colleagues reviewed this for species distribution models and showed that pairwise correlation and variance-inflation screening change which variables, and which shapes, you can defend (Dormann et al. 2013, Ecography 36: 27–46, https://doi.org/10.1111/j.1600-0587.2012.07348.x).

So this repo does not add BIO4, BIO15, or the quarterly layers yet. The next variable is allowed in only after a collinearity check on the cells inside the modeled box: a pairwise absolute correlation, or a variance inflation factor, with a threshold chosen before looking at suitability. Variables that fail that check stay out. Variables that pass can be added beside BIO1 and BIO12, and the spatial-block AUC is the comparison, not a random split.

The check is not in this pass because the two-variable model is the one the service trains. Running it on a 19-layer stack without the screen would hide the problem inside a higher AUC.
