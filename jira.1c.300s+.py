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
from base64 import b64encode
from requests.auth import HTTPBasicAuth

SEARCH = '{host}/issues/?jql={query}'
CACHENAME = '%s-cache.json' % os.path.basename(__file__).split('.')[0]
CACHEFILE = os.path.join(os.path.dirname(__file__), CACHENAME)
cache = {}  # global cache object

ASSIGNED_ISSUES = 'assignee = currentUser() AND statusCategory != done ORDER BY issueType'
WATCHED_ISSUES = 'watcher = currentUser() AND statusCategory != done ORDER BY updated DESC'
RECENT_ISSUES = 'issuekey in issueHistory() ORDER BY lastViewed DESC'


def _get_jira_auth():
    """ Fetch Jira authentication token. """
    with open(os.path.expanduser('~/.config/atlassian.json')) as handle:
        CONFIG = json.load(handle)
    host = CONFIG['jira']['host']
    auth = HTTPBasicAuth(*CONFIG['jira']['auth'].split(':'))
    return host, auth


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


def _get_issues(host, auth, query, debug=False):
    """ Get issues from the server. """
    try:
        issues = []
        url = f'{host}/rest/api/2/search?fields=summary,issuetype&jql={query}'
        response = requests.get(url, auth=auth)
        for issue in response.json()['issues']:
            if opts.debug:
                print(json.dumps(issue, indent=2))
            key = issue['key']
            href = issue['self']
            summary = issue['fields']['summary']
            img = _get_image(issue['fields']['issuetype'])
            issues.append((key, summary, href, img))
        return issues
    except Exception as err:
        print(f'Err\n---\n{err}')
        raise SystemExit()


def titleize(count, suffix):
    """ Pluralize the title. """
    if count == 0:
        return f'{suffix}s'
    suffix += 's' if count != 1 else ''
    return f'{count} {suffix}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jira script for Argos')
    parser.add_argument('--debug', default=False, action='store_true', help='enable debug logging')
    opts = parser.parse_args()
    # Display the Argos output
    host, auth = _get_jira_auth()
    issues = _get_issues(host, auth, ASSIGNED_ISSUES, opts.debug)
    watched = _get_issues(host, auth, WATCHED_ISSUES, opts.debug)
    recent = _get_issues(host, auth, RECENT_ISSUES, opts.debug)
    # Assigned Issues
    print(f'{titleize(len(issues), "Issue")}\n---')
    for key, summary, href, img in issues:
        print(f'{key} - {summary[:60].strip()} | href="{host}/browse/{key}" image="{img}"')
    if not issues:
        print(f'No assigned issues | color=#888')
    # Watched Issues and Escalations
    print(f'---\nWatching {len(watched)} Issues')
    for key, summary, href, img in watched[:10]:
        print(f'-- {key} - {summary[:60].strip()} | size=10 color=#bbb href="{host}/browse/{key}" image="{img}"')
    # Recently Viewed Issues
    print('Recently Viewed Issues')
    for key, summary, href, img in recent[:10]:
        print(f'-- {key} - {summary[:60].strip()} | size=10 color=#bbb href="{host}/browse/{key}" image="{img}"')
    url = SEARCH.replace('{host}', host).replace('{query}', ASSIGNED_ISSUES)
    print(f'Go to Jira {" "*160}<span color="#444">.</span>| href="{url}"')
