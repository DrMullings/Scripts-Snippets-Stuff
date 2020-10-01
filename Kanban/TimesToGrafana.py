#!/usr/bin/env python3
#==============================================================================

from redminelib import Redmine
import pdb
import datetime
import time
import logging
import json
import statistics
import configparser
from influxdb import InfluxDBClient
import sys

config = configparser.ConfigParser()
config.read('config_do_never_push.ini')

REDMINE_URL = config['REDMINE']['URL']
REDMINE_KEY = config['REDMINE']['ApiKey']

INFLUX_HOST = config['INFLUX']['Host']
INFLUX_PORT = config['INFLUX']['Port']
INFLUX_USER = config['INFLUX']['User']
INFLUX_PASS = config['INFLUX']['Pass']
INFLUX_DATABASE = config['INFLUX']['Database']

try:
    redmine = Redmine(REDMINE_URL, key=REDMINE_KEY)
    influx = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, username=INFLUX_USER, password=INFLUX_PASS, database=INFLUX_DATABASE)
except Exception as e:
    print("Exception when connecting to Databases ",e)
    sys.exit(1)

prjlist = ['suseqa', 'openqav3', 'openqatests']
taglist = [ 'epic', 'saga', 'fate']
points = []

time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

#create result dictionary
results = {}
for prj in prjlist:
    results[prj] = {}
 
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

def create_point(prj, medianLeadTime, meanLeadTime, medianCycleTime, meanCycleTime):
    point = {
        "measurement": prj,
        "time": time,
        #"time": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fields": {
            "MedianLeadTime": float(medianLeadTime),
            "MeanLeadTime":float(meanLeadTime),
            "MedianCycletime": float(medianCycleTime),
            "MeanCycleTime": float(meanCycleTime),
                }
            }
    return point

try:
    for prj in prjlist:
        tickets = redmine.issue.filter(project_id=prj, status_id=id_codes["Resolved"])

        prjLeadList = []
        prjCycList = []

        for tckt in tickets:
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
            leadTime = leadTime.days

            if prgDate:
                cycTime = endDate - prgDate
                cycTime = cycTime.days
            else:
                cycTime = None

            prjLeadList.append(leadTime)
            if (cycTime):
                 prjCycList.append(cycTime)

        prjMedianLead = statistics.median(prjLeadList)
        prjMeanLead = statistics.mean(prjLeadList)
        prjMedianCyc = statistics.median(prjCycList)
        prjMeanCyc = statistics.mean(prjCycList)
        point = create_point(prj, prjMedianLead, prjMeanLead, prjMedianCyc, prjMeanCyc)
        points.append(point)

except Exception as e:
    print("Exception during parsing ", e)
    sys.exit(2)

#push to influxdb

influx.write_points(points, time_precision='s', database=INFLUX_DATABASE, retention_policy=None, tags=None, batch_size=None, protocol=u'json', consistency=None)

