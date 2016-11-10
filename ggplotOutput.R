library(ggplot2)
library(dplyr)
setwd("~/habitat-ABM/")
agents <- read.csv("output.csv")
theme_set(theme_bw(14))
ggplot(agents, aes(x=x, y=y)) + stat_bin_2d(aes(fill=..count..))

fossilProp <- agents %>% 
  group_by(x, y) %>%
  mutate(cellCount = n()) %>%
  summarize(perGrazers = unique(sum(habitat_preference == "Grassland")/cellCount))

ggplot(fossilProp, aes(x,y,fill=perGrazers)) + 
  geom_raster()
