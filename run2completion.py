from habitat_model import *
import os

size=25
n=500
range=5
outdir="/Users/wabarr/habitat-ABM/testRun/"
worldfilename = "patchyworld.csv"

os.makedirs(outdir)

os.system("Rscript /Users/wabarr/habitat-ABM/command_makeworld.R %d %d %s %s" %(size, range, outdir, worldfilename))

mod = HabitatModel(height=size, width=size, N=n, method="fromFile", filename=worldfilename, outdir=outdir)

while mod.running:
    mod.step()

os.system("Rscript /Users/wabarr/habitat-ABM/command_plotFossilOutput.R %s %s " %(outdir, worldfilename))