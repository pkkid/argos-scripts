#!/usr/bin/env python3
"""
JIRA Open Issues.

References:
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import requests, subprocess, shlex
from requests.auth import HTTPBasicAuth

ASSIGNED_ISSUES = 'assignee = currentUser() AND statusCategory != done'


def _get_jira_auth():
    """ Authenticate with JIRA. """
    # Auth needs to be defined in some ~/.bash* file with the format:
    # export JIRA_AUTH="user@nasuni.com:API_TOKEN"
    host, auth = None, None
    result = subprocess.check_output(shlex.split(f'bash -c "grep JIRA_....= ~/.bash*"'))
    result = result.decode('utf8').strip()
    for line in result.split('\n'):
        if 'JIRA_HOST' in line:
            host = line.rsplit('=', 1)[-1].strip('"')
        if 'JIRA_AUTH' in line:
            authstr = line.rsplit('=', 1)[-1]
            email, token = authstr.strip('"').split(':', 1)
            auth = HTTPBasicAuth(email, token)
    if not host:
        print(f'Err\n---\nUnable to find JIRA_HOST in environment.')
        raise SystemExit()
    if not auth:
        print(f'Err\n---\nUnable to find JIRA_AUTH in environment.')
        raise SystemExit()
    return host, auth


def _get_issues(host, auth, query):
    """ Get issues from the server. """
    try:
        issues = []
        url = f'{host}/rest/api/2/search?fields=summary&jql={query}'
        response = requests.get(url, auth=auth)
        for issue in response.json()['issues']:
            key = issue['key']
            summary = issue['fields']['summary']
            href = issue['self']
            issues.append((key, summary, href))
        return issues
    except Exception as err:
        print(f'Err\n---\n{err}')
        raise SystemExit()


def _print_title(prs):
    """ Pluralize the title. """
    total = len(prs)
    title = f'{total} Issues'
    if total == '0': title = 'No Issues'
    if total == 1: title = '1 Issue'
    print(title)
    

if __name__ == '__main__':
    host, auth = _get_jira_auth()
    assigned = _get_issues(host, auth, ASSIGNED_ISSUES)
    _print_title(assigned)
    print('---')
    for key, summary, href in assigned:
        print(f'{key} - {summary[:40].strip()} | href="{host}/browse/{key}"')
    if not assigned:
        print(f'No pull requests | color=#888')
