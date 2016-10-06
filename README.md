
### general.db
Tables:
* `last_updated`
* `job_extrainfo`
* `project_raw`
* `corehour_weekly`
* `corehour_monthly`
* `storage_history`
* `jobs`
* `corehour_history`
* `projects`


#### general.db > jobs
Fields:
* `date`
* `job_id`
* `proj_id`
* `user`
* `start`
* `end`
* `partition`
* `cores`
* `cluster`
* `nodes`
* `jobname`
* `jobstate`

Typical output:
```
"2016-04-15 15:17:00",
7558164,
"b2013064",
"chuanw",
1460722611,
1462016,
"node",
16,
"milou",
"m32",
"P4105_201_alignment",
"TIMEOUT"
```


### efficiency.db
Tables:
* `jobs`
* `last_updated`

#### efficiency.db > jobs
Fields:
* `job_id`
* `cluster`
* `proj_id`
* `user`
* `cpu_mean`
  * The mean cpu usage of the job, all time points and all cores included. Normalised by # booked cores, so 0-100%.
* `cpu_cores_used_percentile`
  * Don't use this value. It counts the 75th percentile of how many cpus that were active simultaneously over all time points.
* `cores`
  * The number of cores the job had booked.
* `mem_peak`
  * The peak RAM usage during the job (Gb)
* `mem_median`
  * Median RAM usage (Gb)
* `mem_limit`
  * The amount of RAM the job had access to (8GB per core on ordinary nodes).
* `counts`
  * The number of measurement points we have collected during the job (taken roughly every 5 minutes).
* `state`
* `date_finished`
* `nodelist`

Typical output:
```
8634368,
"milou",
"b2013064",
"chuanw",
22.925,
2.25,
4,
3.1,
3.1,
32.0,
8.0,
"CANCELLED",
"2016-09-20",
"m104 "
```
