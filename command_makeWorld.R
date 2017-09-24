args = commandArgs(trailingOnly = TRUE)
library(simulateSpatialData)

size=as.integer(args[1])
range=as.integer(args[2])
outdir = args[3]
worldfilename = args[4]


world = makeWorld(size=size, range=range, returnDF=TRUE)
write.table(x=world, file=paste(outdir, worldfilename, sep="/"), row.names=FALSE)