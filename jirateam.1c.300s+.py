#!/usr/bin/env python3
# encoding: utf-8
"""
JIRA Team Issues.
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import argparse
import jstyleson
import os
import requests
from base64 import b64encode, b64decode
from collections import defaultdict
from requests.auth import HTTPBasicAuth

SEARCH = '{host}/issues/?filter={filterid}'
CACHENAME = '%s-cache.json' % os.path.basename(__file__).split('.')[0]
CACHEFILE = os.path.join(os.path.dirname(__file__), CACHENAME)
FILTER_ID = None
cache = {}  # global cache object


def _getkey(lookup):
    """ Fetch the specified key. """
    group, name = lookup.lower().split('.')
    for path in ('~/.config/keys.jsonc', '~/Private/keys/keys.jsonc'):
        filepath = os.path.expanduser(path)
        if not os.path.exists(filepath): continue  # noqa
        with open(filepath, 'r') as handle:
            value = jstyleson.load(handle).get(group, {}).get(name)
            if value is None: continue  # noqa
            if not value.startswith('b64:'): return value  # noqa
            return b64decode(value[4:]).decode('utf8')
    raise Exception(f'Key not specified: {lookup}')


def _get_jira_auth():
    """ Fetch Jira authentication token. """
    host = _getkey('jira.host')
    auth = HTTPBasicAuth(*_getkey('jira.auth').split(':'))
    filterid = _getkey('jira.team_filter')
    return host, auth, filterid


def _get_image(issuetype):
    """ Fetch the image for the specified issuetype. """
    global cache
    if not cache and os.path.isfile(CACHEFILE):
        with open(CACHEFILE, 'r') as handle:
            cache = jstyleson.load(handle)
    if issuetype['name'] not in cache:
        img = requests.get(issuetype['iconUrl'])
        imgstr = b64encode(img.content).decode('utf8')
        cache[issuetype['name']] = imgstr
        with open(CACHEFILE, 'w') as handle:
            jstyleson.dump(cache, handle)
    return cache[issuetype['name']]


def _get_issues(host, auth, filterid, debug=False):
    """ Get issues from the server. """
    try:
        # Get the JQL Query from the api
        issues = defaultdict(list)
        jql = requests.get(f'{host}/rest/api/2/filter/{filterid}', auth=auth).json()['jql']
        url = f'{host}/rest/api/2/search?fields=summary,issuetype,assignee,status&jql={jql}'
        response = requests.get(url, auth=auth)
        for issue in response.json()['issues']:
            if opts.debug:
                print(jstyleson.dumps(issue, indent=2))
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
    host, auth, filterid = _get_jira_auth()
    issues = _get_issues(host, auth, filterid, opts.debug)
    print(f'Team\n---')
    for name in sorted(issues.keys()):
        print(f"{name} <span color='#888'>({len(issues[name])} issues)</span>")
        for key, summary, href, img, status in issues[name][:10]:
            print(f'-- {status.upper()} - {key} - {summary[:50].strip()} | size=10 color=#bbb href="{host}/browse/UNTY-{key}" image="{img}"')  # noqa
    if not issues:
        print(f'No pull requests | color=#888')
    url = SEARCH.replace('{host}', host).replace('{filterid}', filterid)
    print(f'---\nGo to Jira {" "*160}<span color="#444">.</span>| href="{url}"')
