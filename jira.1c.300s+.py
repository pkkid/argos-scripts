#!/usr/bin/env python3
# encoding: utf-8
"""
JIRA Open Issues.
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import argparse, json, os, requests, subprocess, shlex
from base64 import b64encode
from requests.auth import HTTPBasicAuth

ASSIGNED_ISSUES = 'assignee = currentUser() AND statusCategory != done'
SEARCH = '{host}/issues/?jql={query}'
CACHENAME = '%s-cache.json' % os.path.basename(__file__).split('.')[0]
CACHEFILE = os.path.join(os.path.dirname(__file__), CACHENAME)
cache = {}  # global cache object


def _get_jira_auth():
    """ Authenticate with JIRA. """
    # Auth needs to be defined in some ~/.bash* file with the format:
    # export JIRA_HOST="host"
    # export JIRA_AUTH="user@example.com:token"
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
            if opts.debug: print(json.dumps(issue, indent=2))
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
    if count == 0: return f'{suffix}s'
    suffix += 's' if count != 1 else ''
    return f'{count} {suffix}'
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jira script for Argos')
    parser.add_argument('--debug', default=False, action='store_true', help='enable debug logging')
    opts = parser.parse_args()
    # Display the Argos output
    host, auth = _get_jira_auth()
    issues = _get_issues(host, auth, ASSIGNED_ISSUES, opts.debug)
    print(f'{titleize(len(issues), "Issue")}\n---')
    for key, summary, href, img in issues:
        print(f'{key} - {summary[:60].strip()} | href="{host}/browse/{key}" image="{img}"')
    if not issues:
        print(f'No pull requests | color=#888')
    url = SEARCH.replace('{host}', host).replace('{query}', ASSIGNED_ISSUES)
    print(f'Go to Jira | href="{url}"')
