#!/usr/bin/env python

""" project_stats.py
Connects to UPPMAX jobstats sqlite databases and fetches information about
jobs (filtered by input args). Outputs these metrics to a static file for
downstream use.

All jobstats are saved as files in /sw/share/slurm/<cluster>/uppmax_jobstats/
for 30 days. Martin Dahlo then saves all of these permanently into three databases:

* /proj/b2013023/statistics/general/general.sqlite
    > contains general info about jobs and projects - this is probably where
    > you could find your data to filter on.
    > cluster and jobid make a primary key for individual jobs

* /proj/b2013023/statistics/job_efficiency/job_efficiency.sqlite
    > processed efficiency values, that summarize each job to a few numbers, but
    > not a timeline like in the jobstats plots.  It can be used to quickly get the efficiency info.

On tools, we filter for these UPPMAX projects:
* a2010002
* a2015205
* a2012043
* b2013064
* ngi2016004
* ngi2016003

Author: Phil Ewels <phil.ewels@scilifelab.se>
Started: 29-09-2016
"""

from __future__ import print_function
import click
import json
import logging
import os
import time
import shutil
import sqlite3

__version__ = 0.1

config = {
    'general.db': '/proj/b2013023/statistics/general/general.sqlite',
    'efficiency.db': '/proj/b2013023/statistics/job_efficiency/job_efficiency.sqlite',
    'stats.db': '/proj/b2013023/statistics/job_stats_raw/stats',
}

@click.command(
    context_settings = dict( help_option_names = ['-h', '--help'] )
)
@click.option('-A', '--project', 'projects',
    type = str,
    multiple = True,
    help = "UPPMAX Project ID to filter for. You can specify multiple projects by repeating this flag."
)
@click.option('-d', '--days',
    type = int,
    help = "Number of days' statistics to fetch, counted back from now."
)
@click.option('-o', '--jobstats_dir',
    type = str,
    default = 'jobstat_files',
    help = "Directory to save jobstats files to. Default: jobstat_files"
)
@click.option('-q', '--quiet',
    is_flag = True,
    help = "Suppress log messages"
)
@click.option('-v', '--verbose',
    is_flag = True,
    help = "Verbose output"
)
@click.version_option(__version__)

def fetch_stats(projects, days, jobstats_dir, quiet, verbose):
    
    # Set up the log
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    
    logging.info("Fetching {} days of jobstats for projects : {}".format(days, ', '.join(projects)))
    
    # Set up variables
    jobs = list()
    node_jobs = dict()
    
    # Connect to the general database
    logging.debug("Connecting to the general database")
    general_conn = sqlite3.connect(config['general.db'])
    logging.debug("  ..connected")
    
    # Fetch jobs from this project
    general_query = "SELECT * from jobs"
    if days is not None:
        timestamp = int(time.time())
        since = timestamp - (days*24*60*60)
        general_query += " WHERE start > {}".format(since)
    if len(projects) > 0:
        general_query += " and proj_id IN ('{}')".format("','".join(projects))
    logging.debug("Running query: {}".format(general_query))
    cursor = general_conn.execute(general_query)
    for row in cursor:
        jobs.append({
            'date': row[0],
            'job_id': row[1],
            'proj_id': row[2],
            'user': row[3],
            'start': row[4],
            'end': row[5],
            'partition': row[6],
            'cores': row[7],
            'cluster': row[8],
            'nodes': row[9],
            'jobname': row[10],
            'jobstate': row[11],
        })
        if not row[9] in node_jobs:
            node_jobs[row[9]] = list()
        node_jobs[row[9]].append(row[1])
    
    logging.info("Found {} jobs spread across {} nodes".format(len(jobs), len(node_jobs)))
    
    # Close general database
    general_conn.close()
    
    # Connect to the job summary stats database
    logging.debug("Connecting to the job efficiency stats database")
    efficiency_conn = sqlite3.connect(config['efficiency.db'])
    logging.debug("  ..connected")
    
    # Get job summary stats - NB: Job IDs not unique across different clusters!
    # list_tables(efficiency_conn)
    count_none = 0
    for idx, job in enumerate(jobs):
        if idx % 100 == 0:
          logging.debug("Getting summary stats for job {} of {}".format(idx, len(jobs)))
        efficiency_query = "SELECT * from jobs WHERE job_id = '{}' AND proj_id = '{}' AND user = '{}'".format(job['job_id'], job['proj_id'], job['user'])
        # logging.debug("Running query: {}".format(efficiency_query))
        cursor = efficiency_conn.execute(efficiency_query)
        row = cursor.fetchone()
        try:
            # jobs[idx]['job_id'] = row[0]
            # jobs[idx]['cluster'] = row[1]
            # jobs[idx]['proj_id'] = row[2]
            jobs[idx]['user'] = row[3]
            jobs[idx]['cpu_mean'] = row[4]
            jobs[idx]['cpu_cores_used_percentile'] = row[5]
            # jobs[idx]['cores'] = row[6]
            jobs[idx]['mem_peak'] = row[7]
            jobs[idx]['mem_median'] = row[8]
            jobs[idx]['mem_limit'] = row[9]
            jobs[idx]['counts'] = row[10]
            # jobs[idx]['state'] = row[11]
            jobs[idx]['date_finished'] = row[12]
            # jobs[idx]['nodelist'] = row[13]
        except TypeError:
            count_none += 1
            logging.debug("No results found for job {} ({}, {})".format(job['job_id'], job['proj_id'], job['user']))
    
    logging.info("Found results for {} out of {} jobs".format(len(jobs)-count_none, len(jobs)))
    
    # Close efficiency stats database
    efficiency_conn.close()
    
    # Print parsed data to stdout
    print(json.dumps(jobs))
    
    # Copy the jobstat files to a directory
    logging.debug("Starting to copy files to {}".format(jobstats_dir))
    num_copied = 0
    num_existed = 0
    for job in jobs:
        src = "/sw/share/slurm/{}/uppmax_jobstats/{}/{}".format(job['cluster'], job['nodes'], job['job_id'])
        dst = os.path.join(jobstats_dir, job['cluster'], job['nodes'], str(job['job_id']))
        try:
            os.makedirs(os.path.dirname(dst))
        except OSError:
            pass
        if os.path.isfile(dst):
            num_existed += 1
        else:
            try:
                shutil.copyfile(src, dst)
                num_copied += 1
            except IOError:
                pass
    logging.info("Copied jobstats files for {} out of {} jobs ({} already there)".format(num_copied, len(jobs), num_existed))


def list_tables(db_conn):
    """ Helper function for probing database structure """
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for tab in tables:
        t = tab[0]
        print ("TABLE: {}".format(t))
        if t == 'jobs':
            cursor.execute("PRAGMA table_info({});".format(t))
            print(json.dumps(cursor.fetchall(), indent=4))
            print("\n\n")


if __name__ == "__main__":
    fetch_stats()
