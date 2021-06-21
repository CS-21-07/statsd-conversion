# Statsd.config Conversion Script

## The Purpose of this Program 
This repo contains two scripts. The first (V1) is a script which can convert configuration files exactly to the specifications
currently required by the Graphing Utility created by CS21-07. However, those specificaitons seem largely insufficient for more
generalized purposes of the graphing utility. This is for two reasons:

1. Currently, only certain sections of the config file were converted and made accessible to the front-end. These areas are
	the graphs, graph titles, and available datasources. This is very limiting and,
2. Configuration information is spread across 3 files and are design decisions regarding json structure is not documented.
	There could be inconsistencies.

Therefore, the second script (V2) was created as a much more robust solution which renders the whole configuration file as
json. 

## How to use
V1 is used to update specifically the graph.json which the original version of the graphing utility depends upon to get graph
info. V2 is my proposed (hopefully more generalizable) solution going forward, which generates one json file that has a different
format than what is currently ingested by the graphing utility. However, with very slight modifications to graphing utility
source, this V2 json file will probably be more useful in the future. Therefore, while I will leave V1 in this repo, I would 
reccommend that any time a configuration file needs to be converted, use V2 and adapt code to work with that.

## Input/Output
Input is in the form of a file called 'statsd.conf' held inside the /Config/
Output is in the form of a json file called 'statsd.conf.json' and is viewable in the top-level directory'
