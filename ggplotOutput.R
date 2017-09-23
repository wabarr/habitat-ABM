library(ggplot2)
library(dplyr)
setwd("~/habitat-ABM/")
agents <- read.csv("output.csv")
theme_set(theme_bw(14))

length(agents$AgentID) == length(unique(agents$AgentID))

agentDensity <- ggplot(agents, aes(x=x, y=y)) + 
  stat_bin_2d(aes(fill=..count..)) + 
  labs(title="agent density") + 
  theme(legend.position = "bottom")

fossilProp <- agents %>% 
  group_by(x, y) %>%
  mutate(cellCount = n()) %>%
  summarize(perGrazers = unique(sum(habitat_preference == "Grassland")/cellCount))

perGrazers <- ggplot(fossilProp, aes(x,y,fill=perGrazers)) + 
  geom_raster() + 
  labs(title="percent grazers") + 
  theme(legend.position = "bottom")

gridExtra::grid.arrange(agentDensity,perGrazers, ncol=2)
