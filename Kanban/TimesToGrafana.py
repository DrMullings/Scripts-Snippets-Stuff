#!/usr/bin/env python3
#==============================================================================

from redminelib import Redmine
import pdb
import datetime
import logging
import json
import statistics
import configparser
from influxdb import InfluxDBClient

config = configparser.ConfigParser()
config.read('config_do_never_push.ini')

REDMINE_URL = config['REDMINE']['URL']
REDMINE_KEY = config['REDMINE']['ApiKey']

INFLUX_HOST = config['INFLUX']['Host']
INFLUX_PORT = config['INFLUX']['Port']
INFLUX_USER = config['INFLUX']['User']
INFLUX_PASS = config['INFLUX']['Pass']
INFLUX_DATABASE = config['INFLUX']['Database']

redmine = Redmine(REDMINE_URL, key=REDMINE_KEY)
influx = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, username=INFLUX_USER, password=INFLUX_PASS, database=INFLUX_DATABASE)

prjlist = ['suseqa', 'openqav3', 'openqatests']
taglist = [ 'epic', 'saga', 'fate']
cycleList = []
leadList = []

id_codes = {
        'New' : '1',
        'In Progress' : '2',
        'Resolved' : '3',
        'Feedback' : '4',
        'Workable' : '12'
        }


def went_in_progress(jsn):
    if jsn.get("name", "invalid_default") == "status_id":
        if jsn["new_value"] == id_codes.get("In Progress"):
            return jsn["old_value"] in [id_codes["Workable"], id_codes["New"]]
    return False

def is_story(tckt):
    if any(s in tckt.subject for s in taglist):
        return False
    return True

for prj in prjlist:
    tickets = redmine.issue.filter(project_id=prj, status_id=id_codes["Resolved"])

    for tckt in tickets:
        # only consider normal [u] tickets
        if not is_story(tckt):
            continue

        crtDate = tckt.created_on
        endDate = tckt.closed_on
        # set an invalid default
        prgDate = None

        journals = tckt.journals
        for jrn in journals:
            try:
                # look at first entry to not get an array
                jDetails = json.loads(json.dumps(jrn.details[0]))
            except:
                # empty details
                continue
            if went_in_progress(jDetails):
                prgDate = jrn.created_on
                #print("Went in progress: " + str(prgDate))
                break

        leadTime = endDate - crtDate
        leadList.append(leadTime.days)

        if prgDate:
            cycTime = endDate - prgDate
            cycleList.append(cycTime.days)

meanCycTime = statistics.mean(cycleList)
medianCycTime = statistics.median(cycleList)

meanLeadTime = statistics.mean(leadList)
medianLeadTime = statistics.median(leadList)

points = [
            {
                "measurement": "Times",
                "time": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "MeanCycleTime": meanCycTime,
                    "MedianCycleTime": medianCycTime,
                    "MeanLeadTime": meanLeadTime,
                    "MediaLeadTime": medianLeadTime
                }
            }
        ]


#push to influxdb

influx.write_points(points, time_precision='ms', database=INFLUX_DATABASE, retention_policy=None, tags=None, batch_size=None, protocol=u'json', consistency=None)

