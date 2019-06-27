#!/usr/bin/env python3
"""
Bitbucket Pull Requests

References:
  Argos Extension: https://extensions.gnome.org/extension/1176/argos/
  Argos Documentation: https://github.com/p-e-w/argos
"""
import requests, subprocess, shlex
from requests.auth import HTTPBasicAuth

PRS = '{host}/rest/api/latest/inbox/pull-requests?role=%s&start=0' \
    '&limit=10&avatarSize=64&withAttributes=true&state=OPEN&order=oldest'


def _get_bitbucket_auth():
    """ Authenticate with JIRA. """
    # Auth needs to be defined in some ~/.bash* file with the format:
    # export BITBUCKET_HOST="host"
    # export BITBUCKET_AUTH="user:token"
    host, auth = None, None
    result = subprocess.check_output(shlex.split(f'bash -c "grep BITBUCKET_....= ~/.bash*"'))
    result = result.decode('utf8').strip()
    for line in result.split('\n'):
        if 'BITBUCKET_HOST' in line:
            host = line.rsplit('=', 1)[-1].strip('"')
        if 'BITBUCKET_AUTH' in line:
            authstr = line.rsplit('=', 1)[-1]
            user, token = authstr.strip('"').split(':', 1)
            auth = HTTPBasicAuth(user, token)
    if not host:
        print(f'Err\n---\nUnable to find BITBUCKET_HOST in environment.')
        raise SystemExit()
    if not auth:
        print(f'Err\n---\nUnable to find BITBUCKET_AUTH in environment.')
        raise SystemExit()
    return host, auth


def _getprs(host, auth, role):
    """ Get pull requests. role must be one of AUTHOR, REVIEWER. """
    try:
        prs = []
        url = PRS.replace('{host}', host)
        response = requests.get(url, auth=auth)
        response = response.json()
        if response.get('errors'):
            raise Exception(response['errors'][0].get('message', 'Error fetching prs'))
        for pr in response['values']:
            title = pr['title']
            href = pr['links']['self'][0]['href']
            prs.append((title, href))
        return prs
    except Exception as err:
        print(f'Err\n---\n{err}')
        raise SystemExit()


def _print_title(prs):
    """ Pluralize the title. """
    total = len(prs)
    title = f'{total} PRs'
    if total == '0': title = 'No PRs'
    if total == 1: title = '1 PR'
    print(title)
    

if __name__ == '__main__':
    host, auth = _get_bitbucket_auth()
    prs = _getprs(host, auth, 'AUTHOR')
    prs += _getprs(host, auth, 'REVIEWER')
    _print_title(prs)
    print('---')
    for title, href in prs:
        print(f'{title[:60].strip().lower()} | href="{href}"')
    if not prs:
        print(f'No pull requests | color=#888')
