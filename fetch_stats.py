#!/usr/bin/env python

""" fetch_stats.py
Connects to UPPMAX jobstats sqlite databases and fetches information about
jobs (filtered by input args). Outputs these metrics to a static file for
downstream use.

All jobstats are saved as files in /sw/share/slurm/<cluster>/uppmax_jobstats/
for 30 days. Martin Dahlo then saves all of these permanently into three databases:

*  /proj/b2013023/statistics/general/general.sqlite
  > contains general info about jobs and projects - this is probably where
  > you could find your data to filter on.
  > cluster and jobid make a primary key for individual jobs

*  /proj/b2013023/statistics/job_efficiency/job_efficiency.sqlite
  > processed efficiency values, that summarize each job to a few numbers, but
  > not a timeline like in the jobstats plots.  It can be used to quickly get the efficiency info.

*  /proj/b2013023/statistics/job_stats_raw/stats
  > contains the raw jobstats data which can be used to do the timeline
  > these stats are in a slightly more complex format though - the database is sharded into one
  > database per node since there are so many jobs ant the raw data is quite fluffy. It was very
  > slow to have them all in a single sqlite db so i created a sqlite file for each node.
  > They are all identical in structure inside
  > so you'll have to have the node name the job ran on (from general.sqlite), then open a connection to it and query the db

Author: Phil Ewels <phil.ewels@scilifelab.se>
Started: 29-09-2016
"""

from __future__ import print_function
import click
import json
import logging
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
@click.option('-A', '--proj',
    required = True,
    type = str,
    help = "Filter by project ID."
)
@click.option('-j', '--job',
    type = int,
    help = "Return specific job number only"
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

def fetch_stats(proj, job, quiet, verbose):
    
    # Set up the log
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Connect to the general database
    logging.debug("Connecting to the general database")
    general_conn = sqlite3.connect(config['general.db'])
    
    # Fetch jobs of interest
    cursor = general_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    # cursor = conn.execute("SELECT id, name, address, salary  from COMPANY")
    # for row in cursor:
    #    print "ID = ", row[0]
    #    print "NAME = ", row[1]
    #    print "ADDRESS = ", row[2]
    #    print "SALARY = ", row[3], "\n"
    
    # Close general database
    general_conn.close()
    


if __name__ == "__main__":
    fetch_stats()
