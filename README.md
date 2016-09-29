
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
* `cpu_cores_used_percentile`
* `cores`
* `mem_peak`
* `mem_median`
* `mem_limit`
* `counts`
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
