#!/usr/bin/env python3
# encoding: utf-8
"""
JIRA Open Issues.
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import argparse
import json
import os
import requests
import shlex
import subprocess
from base64 import b64encode
from collections import defaultdict
from requests.auth import HTTPBasicAuth

SEARCH = '{host}/issues/?filter={filter_id}'
CACHENAME = '%s-cache.json' % os.path.basename(__file__).split('.')[0]
CACHEFILE = os.path.join(os.path.dirname(__file__), CACHENAME)
FILTER_ID = None
cache = {}  # global cache object


def _get_jira_auth():
    """ Authenticate with JIRA. """
    # Auth needs to be defined in some ~/.bash* file with the format:
    # export JIRA_HOST="host"
    # export JIRA_AUTH="user@example.com:token"
    # export JIRA_TEAM=12345  # filter id of search
    global JIRATEAM_FILTER_ID
    host, auth, filter_id = None, None, None
    result = subprocess.check_output(shlex.split(f'bash -c "grep JIRA_....= ~/.bash*"'))
    result = result.decode('utf8').strip()
    for line in result.split('\n'):
        if 'JIRA_HOST' in line:
            host = line.rsplit('=', 1)[-1].strip('"')
        if 'JIRA_AUTH' in line:
            authstr = line.rsplit('=', 1)[-1]
            email, token = authstr.strip('"').split(':', 1)
            auth = HTTPBasicAuth(email, token)
        if 'JIRA_TEAM' in line:
            filter_id = line.rsplit('=', 1)[-1].strip('"')
    # Check we found all values
    for name, value in (('JIRA_HOST', host), ('JIRA_AUTH', auth), ('JIRA_TEAM', filter_id)):
        if not value:
            print(f'Err\n---\nUnable to find {name} in environment.')
            raise SystemExit()
    return host, auth, filter_id


def _get_image(issuetype):
    """ Fetch the image for the specified issuetype. """
    global cache
    if not cache and os.path.isfile(CACHEFILE):
        with open(CACHEFILE, 'r') as handle:
            cache = json.load(handle)
    if issuetype['name'] not in cache:
        img = requests.get(issuetype['iconUrl'])
        imgstr = b64encode(img.content).decode('utf8')
        cache[issuetype['name']] = imgstr
        with open(CACHEFILE, 'w') as handle:
            json.dump(cache, handle)
    return cache[issuetype['name']]


def _get_issues(host, auth, filter_id, debug=False):
    """ Get issues from the server. """
    try:
        # Get the JQL Query from the api
        issues = defaultdict(list)
        jql = requests.get(f'{host}/rest/api/2/filter/{filter_id}', auth=auth).json()['jql']
        url = f'{host}/rest/api/2/search?fields=summary,issuetype,assignee,status&jql={jql}'
        response = requests.get(url, auth=auth)
        for issue in response.json()['issues']:
            if opts.debug:
                print(json.dumps(issue, indent=2))
            key = issue['key'].replace('UNTY-', '')
            href = issue['self']
            summary = issue['fields']['summary']
            name = issue['fields']['assignee']['displayName']
            img = _get_image(issue['fields']['issuetype'])
            status = issue['fields']['status']['name']
            issues[name].append((key, summary, href, img, status))
        return issues
    except Exception as err:
        print(f'Err\n---\n{err}')
        raise SystemExit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jira script for Argos')
    parser.add_argument('--debug', default=False, action='store_true', help='enable debug logging')
    opts = parser.parse_args()
    # Display the Argos output
    host, auth, filter_id = _get_jira_auth()
    issues = _get_issues(host, auth, filter_id, opts.debug)
    print(f'Teams\n---')
    for name in sorted(issues.keys()):
        print(f"{name} <span color='#888'>({len(issues[name])} issues)</span>")
        for key, summary, href, img, status in issues[name][:10]:
            print(f'-- {status.upper()} - {key} - {summary[:50].strip()} | size=10 color=#bbb href="{host}/browse/UNTY-{key}" image="{img}"')  # noqa
    if not issues:
        print(f'No pull requests | color=#888')
    url = SEARCH.replace('{host}', host).replace('{filter_id}', filter_id)
    print(f'---\nGo to Jira {" "*160}<span color="#444">.</span>| href="{url}"')
