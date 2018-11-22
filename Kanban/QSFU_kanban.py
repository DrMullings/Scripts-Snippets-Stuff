#!/usr/bin/env python3
#==============================================================================

from redminelib import Redmine
import pdb
import datetime
import logging
import json
import statistics
import configparser
import matplotlib
import matplotlib.pyplot as plt


config = configparser.ConfigParser()
config.read('config_do_never_push.ini')

URL = config['API']['URL']
KEY = config['API']['ApiKey']

redmine = Redmine(URL, key=KEY)

prjlist = ['suseqa', 'openqav3', 'openqatests']
taglist = ['y', 'epic', 'saga', 'fate']
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
    u_tickets = [t for t in tickets if '[u]' in t.subject]

    for tckt in u_tickets:
        # only consider normal [u] tickets
        if not is_story(tckt):
            continue

        #try:
        #    print(t.subject)
        #except:
        #    print("Could not print subject")

        crtDate = tckt.created_on
        endDate = tckt.closed_on
        # set an invalid default
        prgDate = None

        #print("Creation date: " + str(crtDate))
        #print("Close date: " + str(endDate))

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
        #print("Lead time " + str(leadTime))
        leadList.append(leadTime.days)

        if prgDate:
            cycTime = endDate - prgDate
            #print("Cycle time: " + str(cycTime))
            cycleList.append(cycTime.days)

meanCycTime = statistics.mean(cycleList)
medianCycTime = statistics.median(cycleList)

meanLeadTime = statistics.mean(leadList)
medianLeadTime = statistics.median(leadList)

print("Mean cycle time: " + str(meanCycTime))
print("Median cycle time: " + str(medianCycTime))
print("Minimum cycle time: " + str(min(cycleList)))
print("Maximum cycle time: " + str(max(cycleList)))

print("Mean lead time: " + str(meanLeadTime))
print("Median lead time: " + str(medianLeadTime))
print("Minimum lead time: " + str(min(leadList)))
print("Maximum lead time: " + str(max(leadList)))

print("Amount of tickets: " + str(len(u_tickets)))


plt.figure(1)

plt.subplot(211)
plt.hist(cycleList)
plt.ylabel("Amount of tickets")
plt.xlabel("Cycletime in days")

plt.subplot(212)
plt.hist(leadList)
plt.ylabel("Amount of tickets")
plt.xlabel("Leadtime in days")

plt.show()
