args=commandArgs(trailingOnly=TRUE)

outdir = args[1]
worldfilename = args[2]

setwd(outdir)

library(ggplot2)
library(dplyr)

agents <- read.csv("fossil-record_output.csv")

theme_set(theme_bw(14))

## plot fossil proportions

fossilProp <- agents %>% 
  group_by(x, y) %>%
  mutate(cellCount = n()) %>%
  summarize(perGrazers = unique(sum(habitat_preference == "Grassland")/cellCount), count=unique(cellCount))

outPlot = ggplot(fossilProp, aes(x, y, color=perGrazers, size=count)) +
  geom_point() + 
  scale_color_gradient(high="#fff200",low="#1db125") +
  coord_fixed()

ggsave(plot=outPlot , filename="fossilrecord.jpg", width=8, height=8)

## plot the worldfile

world = read.table(worldfilename, header=T)

worldplot = ggplot(data=world) +
    geom_raster(aes(x=x, y=y, fill=factor(category))) +
    scale_fill_manual(values=c("#fff200","#1db125")) +
    coord_fixed()

ggsave(plot=worldplot , filename="worldplot.jpg", width=8, height=8)