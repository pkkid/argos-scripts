#!/usr/bin/env python3
# encoding: utf-8
# Argos Extension: https://extensions.gnome.org/extension/1176/argos/
# Argos Documentation: https://github.com/p-e-w/argos
import argparse
import datetime
import json
import os
import requests
from base64 import b64encode
from collections import defaultdict
from getkeys import getkey
from requests.auth import HTTPBasicAuth

SEARCH = '{host}/issues/?filter={filterid}'
CACHENAME = '%s-cache.json' % os.path.basename(__file__).split('.')[0]
CACHEFILE = os.path.join(os.path.dirname(__file__), CACHENAME)
FILTER_ID = None
cache = {}  # global cache object


def _get_jira_auth():
    """ Fetch Jira authentication token. """
    host = getkey('jira.host', prompt=False)
    auth = HTTPBasicAuth(*getkey('jira.auth', prompt=False).split(':'))
    filterid = getkey('jira.team_filter', prompt=False)
    return host, auth, filterid


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


def _get_issues(host, auth, filterid, debug=False):
    """ Get issues from the server. """
    try:
        # Get the JQL Query from the api
        issues = defaultdict(list)
        jql = requests.get(f'{host}/rest/api/2/filter/{filterid}', auth=auth).json()['jql']
        url = f'{host}/rest/api/2/search?fields=summary,issuetype,assignee,status&expand=changelog&jql={jql}'
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
            days = _get_days_in_state(issue)
            issues[name].append((key, summary, href, img, status, days))
        return issues
    except Exception as err:
        print(f'Err\n---\n{err}')
        raise SystemExit()


def _get_days_in_state(issue):
    """ Find the last date state changed. """
    histories = issue.get('changelog', {}).get('histories', [])
    for history in histories:
        for item in history['items']:
            if item['field'] == 'status':
                now = datetime.date.today()
                then = datetime.datetime.strptime(history['created'][:10], '%Y-%m-%d').date()
                return (now - then).days
    return '?'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jira script for Argos')
    parser.add_argument('--debug', default=False, action='store_true', help='enable debug logging')
    opts = parser.parse_args()
    # Display the Argos output
    host, auth, filterid = _get_jira_auth()
    issues = _get_issues(host, auth, filterid, opts.debug)
    print('Team\n---')
    for name in sorted(issues.keys()):
        print(f"{name} <span color='#888'>({len(issues[name])} issues)</span>")
        for key, summary, href, img, status, days in issues[name][:10]:
            print(f'-- {status.upper()} - {key} - {summary[:50].strip()} <span color="#888">({days} days)</span> | size=10 color=#bbb href="{host}/browse/UNTY-{key}" image="{img}"')  # noqa
    if not issues:
        print('No pull requests | color=#888')
    url = SEARCH.replace('{host}', host).replace('{filterid}', filterid)
    print(f'---\nGo to Jira {" "*160}<span color="#444">.</span>| href="{url}"')
