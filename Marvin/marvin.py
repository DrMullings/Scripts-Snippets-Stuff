#!/usr/bin/env python3

from github import Github
import pdb
import configparser
import datetime 
from datetime import date

config = configparser.ConfigParser()
config.read('marvin.ini')

#TOKEN = config['ACCESS']['TOKEN']
#MAXPRAGE = config['']['']
#MAXLASTCOMMENT = config['']['']
USER = config['ACCESS']['user']
PASS = config['ACCESS']['pass']


def prAge (pr):
    # returns the age of the PR in days
    age = date.today() - pr.created_at.date()
    return age.days

def lastCommentAge (pr):
    # return the age of the last comment in days
    if pr.get_issue_comments().totalCount == 0:
        return prAge(pr)
    age = date.today() - pr.get_issue_comments()[pr.get_issue_comments().totalCount-1].updated_at.date()
    return age.days

def isApproved (pr):
    # return if the pr is approved
    reviews = pr.get_reviews()
    for review in reviews:
        if review.state == 'APPROVED':
            return True
    return False


repolist = ['os-autoinst-distri-opensuse', 'os-autoinst-needles-opensuse']
oldPRList = []
forgottenPRList = []
approvedPRList = []

#g = Github(TOKEN)
g = Github(USER,PASS)
org = g.get_organization('os-autoinst')

#pdb.set_trace()

for r in repolist:
    #get pull requests and iterate over them
    repo = org.get_repo(r)
    pulls = repo.get_pulls(state='open')

#    pdb.set_trace()

    for pull in pulls:
        # get age of last comment
        # get age of PR
        #print(str(prAge(pull)))
        
        if prAge(pull) > 5 :
            oldPRList.append(pull.id)
        if lastCommentAge(pull) > 7:
            forgottenPRList.append(pull.id)
        if isApproved(pull):
            approvedPRList.append(pull.id)
        #print(str(pull.title))
        #print(str(pull.number))
        #print(str(pull.created_at))

print(approvedPRList)

# get PRs to repos
# check opening time
# check last comment

