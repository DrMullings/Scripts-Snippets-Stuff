#!/usr/bin/env python3

from github import Github
import pdb
import datetime 
from datetime import date

class GitHub(object):
    def __init__(self, client_id, client_secret, organisation):
        self.cl_id = client_id
        self.cl_secret  = client_secret
        self.organisation = organisation

        self.g = Github(client_id=self.cl_id, client_secret=self.cl_secret)
        self.org = self.g.get_organization(self.organisation)

    def pr_age(self, pr):
        # returns the age of the PR in days
        age = date.today() - pr.created_at.date()
        return age.days

    def last_comment_age(self, pr):
        # return the age of the last comment in days
        if pr.get_issue_comments().totalCount == 0:
            return self.pr_age(pr)
        age = date.today() - pr.get_issue_comments()[pr.get_issue_comments().totalCount-1].updated_at.date()
        return age.days

    def is_approved(self, pr):
        # return if the pr is approved
        reviews = pr.get_reviews()
        for review in reviews:
            if review.state == 'APPROVED':
                return True
        return False

    def is_merged(self, pr):
        return pr.merged

    def repo_get_open_pulls(self, r):
        repo = self.org.get_repo(r)
        return repo.get_pulls(state='open')

    def create_pr_url(self, pr_nmb, repo):
        base_url = "https://github.com/"
        return str(base_url + self.organisation + "/" + str(repo) + "/pull/" + str(pr_nmb))

    def create_pr_comment(self, pr, msg):
        #pr = self.g.get_organization(pr_org).get_repo(pr_repo).get_pull(pr_id)
        pr.create_issue_comment(msg)


    def get_pr_author(self, pr):
        return pr.user

    def get_last_comment_author(self, comment):
        if pr.get_issue_comments().totalCount == 0:
            return pr.user
        return pr.get_isssue_comments()[pr.get_issue_comments().totalCount-1].user.login

